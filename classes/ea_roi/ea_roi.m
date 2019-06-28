classdef ea_roi < handle
    % ROI class to plot niftis on lead dbs resultfig / 3D Matlab figures
    % example:
    % figure; pobj.openedit=1; ea_roi([spm('dir'),filesep,'toolbox',filesep,'OldSeg',filesep,'grey.nii'],pobj); a=light; axis('off','equal')
    % A. Horn
    
    properties (SetObservable)
        niftiFilename % original nifti filename
        nii % nifti loaded
        threshold % threshold to visualize
        color % color of patch
        alpha=0.7 % alpha of patch
        fv % faces and vertices of patch
        sfv % smoothed version
        cdat % color data of patch
        visible='on' % turn on/off
        name % name to be shown
        smooth % smooth by FWHM
        binary % is binary ROI
        hullsimplify % simplify hull
        max % maxvalue in nifti - 0.1 of the way
        min % minvalue in nifti + 0.1 of the way
        controlH % handle to color / threshold control figure
        plotFigureH % handle of figure on which to plot
        patchH % handle of patch
        toggleH % toggle handle
        htH % handle for toggle toolbar
    end
    
    methods
        function obj=ea_roi(niftiFilename,pobj) % generator function
            if exist('niftiFilename','var') && ~isempty(niftiFilename)
                obj.niftiFilename=niftiFilename;
            end
            
            
            
            try
                obj.name=pobj.name;
            catch
                [~,obj.name]=fileparts(obj.niftiFilename);
            end
            
            obj.plotFigureH=gcf;
            
            if exist('pobj','var') && ~isempty(pobj)
                try
                    obj.plotFigureH=pobj.plotFigureH;
                end
            end
            try
                obj.htH=pobj.htH;
            catch
                obj.htH=getappdata(obj.plotFigureH,'addht');
            end
            if isempty(obj.htH) % first ROI
                obj.htH=uitoolbar(obj.plotFigureH);
                setappdata(obj.plotFigureH,'addht',obj.htH);
            end
            
            set(0,'CurrentFigure',obj.plotFigureH);
            % set cdata
            if exist('pobj','var') && ~isempty(pobj)
                try
                    obj.color=pobj.color;
                catch
                    obj.color = ea_uisetcolor;
                end
            else
                obj.color = ea_uisetcolor;
            end
            
            % load nifti
            
            obj.nii=ea_load_nii(obj.niftiFilename);
            if length(unique(obj.nii.img(~isnan(obj.nii.img))))==1
                obj.binary=1;
            else
                obj.nii.img(obj.nii.img==0)=nan;
                obj.nii.img=obj.nii.img-nanmin(obj.nii.img(:)); % set min to zero
                obj.binary=0;
            end
            obj.nii.img(isnan(obj.nii.img))=0;
            options.prefs=ea_prefs;
            obj.max=ea_nanmax(obj.nii.img(~(obj.nii.img==0)));
            obj.min=ea_nanmin(obj.nii.img(~(obj.nii.img==0)));
            maxmindiff=obj.max-obj.min;
            obj.max=obj.max-0.1*maxmindiff;
            obj.min=obj.min+0.1*maxmindiff;
            try
                obj.threshold=pobj.threshold;
            catch
                if obj.binary
                    obj.threshold=obj.max/2;
                else
                    obj.threshold=obj.max-0.5*maxmindiff;
                end
            end
            
            obj.smooth=options.prefs.hullsmooth;
            obj.hullsimplify=options.prefs.hullsimplify;
            set(0,'CurrentFigure',obj.plotFigureH);
            obj.patchH=patch;
            
            obj.toggleH=uitoggletool;
            
            % Get the underlying java object using findobj
            jtoggle = findjobj(obj.toggleH);
            
            % Specify a callback to be triggered on any mouse release event
            set(jtoggle, 'MouseReleasedCallback', {@rightcallback,obj})
            update_roi(obj);
            addlistener(obj,'visible','PostSet',...
                @changeevent);
            addlistener(obj,'color','PostSet',...
                @changeevent);
            addlistener(obj,'threshold','PostSet',...
                @changeevent);
            addlistener(obj,'smooth','PostSet',...
                @changeevent);
            addlistener(obj,'hullsimplify','PostSet',...
                @changeevent);
            addlistener(obj,'alpha','PostSet',...
                @changeevent);
            
            if exist('pobj','var') && isfield(pobj,'openedit') && pobj.openedit
                ea_editroi([],[],obj)
            end
            
        end

    end
    
end


function changeevent(~,event)
update_roi(event.AffectedObject,event.Source.Name);
end


function obj=update_roi(obj,evtnm) % update ROI
if ~exist('evtnm','var')
    evtnm='all';
end
if ismember(evtnm,{'all','threshold','smooth','hullsimplify'}) % need to recalc fv here:
    bb=[0,0,0;size(obj.nii.img)];
    bb=map_coords_proxy(bb,obj.nii);
    gv=cell(3,1);
    for dim=1:3
        gv{dim}=linspace(bb(1,dim),bb(2,dim),size(obj.nii.img,dim));
    end
    [X,Y,Z]=meshgrid(gv{1},gv{2},gv{3});
    
    obj.fv=isosurface(X,Y,Z,permute(obj.nii.img,[2,1,3]),obj.threshold);
    fvc=isocaps(X,Y,Z,permute(obj.nii.img,[2,1,3]),obj.threshold);
    obj.fv.faces=[obj.fv.faces;fvc.faces+size(obj.fv.vertices,1)];
    obj.fv.vertices=[obj.fv.vertices;fvc.vertices];
    
    if obj.smooth
                obj.sfv=obj.fv;

        %obj.sfv=ea_smoothpatch(obj.fv,1,obj.smooth);
    else
        obj.sfv=obj.fv;
    end
    
    if ischar(obj.hullsimplify)
        % get to 700 faces
        simplify=700/length(obj.sfv.faces);
        obj.sfv=reducepatch(obj.sfv,simplify);
        
    else
        if obj.hullsimplify<1 && obj.hullsimplify>0
            
            obj.sfv=reducepatch(obj.sfv,obj.hullsimplify);
        elseif obj.hullsimplify>1
            simplify=obj.hullsimplify/length(obj.fv.faces);
            obj.sfv=reducepatch(obj.sfv,simplify);
        end
    end
    if obj.binary
        obj.cdat=abs(repmat(atlasc,length(obj.sfv.vertices),1) ... % C-Data for surface
            +randn(length(obj.sfv.vertices),1)*2)';
    else
        obj.cdat=isocolors(X,Y,Z,permute(obj.nii.img,[2,1,3]),obj.sfv.vertices);
    end
    
    
end

jetlist=jet;

co=ones(1,1,3);
co(1,1,:)=obj.color;
atlasc=double(rgb2ind(co,jetlist));

% show atlas.
set(0,'CurrentFigure',obj.plotFigureH);
set(obj.patchH,...
    {'Faces','Vertices','CData','FaceColor','FaceAlpha','EdgeColor','FaceLighting','Visible'},...
    {obj.sfv.faces,obj.sfv.vertices,obj.cdat,obj.color,obj.alpha,'none','phong',obj.visible});

% add toggle button:
set(obj.toggleH,...
    {'Parent','CData','TooltipString','OnCallback','OffCallback','State'},...
    {obj.htH,ea_get_icn('atlas',obj.color),stripext(obj.niftiFilename),{@ea_roivisible,'on',obj},{@ea_roivisible,'off',obj},obj.visible});
end


function rightcallback(src, evnt,obj)
if evnt.getButton() == 3
    ea_editroi(src,evnt,obj)
end
end

function ea_editroi(Hobj,evt,obj)
obj.controlH=ea_roicontrol(obj);

end

function ea_roivisible(Hobj,evt,onoff,obj)
obj.visible=onoff;
end
function coords=map_coords_proxy(XYZ,V)

XYZ=[XYZ';ones(1,size(XYZ,1))];

coords=V.mat*XYZ;
coords=coords(1:3,:)';
end

function fn=stripext(fn)
[~,fn]=fileparts(fn);
end
