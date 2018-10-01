function ea_preprocess_fmri(options)

directory=[options.root,options.patientname,filesep];

V=spm_vol([directory,options.prefs.rest]);
signallength=length(V);

%% run sequence of proxyfunctions (below):
ea_realign_fmri(signallength,options); % realign fMRI

ea_newseg(directory,options.prefs.prenii_unnormalized,0,options,1); % Segment anat

ea_coreg_pre2fmri(options); % register pre 2 fmri (for timecourse-extraction).

ea_smooth_fmri(signallength,options); % slightly smooth fMRI data


function ea_realign_fmri(signallength,options)
%% realign fmri.
directory=[options.root,options.patientname,filesep];
if ~exist([directory,'r',options.prefs.rest],'file')
    
    restbackup = ea_niifileparts([directory,options.prefs.rest]);
    copyfile([directory,options.prefs.rest], restbackup);
    
    disp('Realignment of rs-fMRI data...');
    filetimepts = ea_appendVolNum([directory,options.prefs.rest], 1:signallength);
    matlabbatch{1}.spm.spatial.realign.estimate.data = {filetimepts};
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.quality = 1;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.sep = 4;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.fwhm = 5;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.rtm = 1;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.interp = 2;
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.wrap = [0 0 0];
    matlabbatch{1}.spm.spatial.realign.estimate.eoptions.weight = ''; 
%     matlabbatch{1}.spm.spatial.realign.estwrite.data = {filetimepts};
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.quality = 1;
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.sep = 4;
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.fwhm = 5;
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.rtm = 0;
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.interp = 2;
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.wrap = [0 0 0];
%     matlabbatch{1}.spm.spatial.realign.estwrite.eoptions.weight = {''};
%     matlabbatch{1}.spm.spatial.realign.estwrite.roptions.which = [2 1];
%     matlabbatch{1}.spm.spatial.realign.estwrite.roptions.interp = 4;
%     matlabbatch{1}.spm.spatial.realign.estwrite.roptions.wrap = [0 0 0];
%     matlabbatch{1}.spm.spatial.realign.estwrite.roptions.mask = 1;
%     matlabbatch{1}.spm.spatial.realign.estwrite.roptions.prefix = 'r';
    spm_jobman('run',{matlabbatch});
    clear matlabbatch;
    disp('Done.');
    ea_reslice_nii([directory, options.prefs.rest], [directory, 'r',options.prefs.rest], [1,1,1], 0, 0, 1, [], [],0)
    movefile(restbackup, [directory, options.prefs.rest]);
end


function ea_coreg_pre2fmri(options)
directory=[options.root,options.patientname,filesep];
% Disable Hybrid coregistration
coregmethod = options.coregmr.method;
options.coregmr.method = strrep(coregmethod, 'Hybrid SPM & ', '');

% Re-calculate mean re-aligned image if not found
if ~exist([directory, 'mean', options.prefs.rest], 'file')
    ea_meanimage([directory, 'r', options.prefs.rest], ['mean', options.prefs.rest]);
end

% Coregistration
transform = ea_coreg2images(options,...
    [directory,options.prefs.prenii_unnormalized],...
    [directory,'mean',options.prefs.rest],...
    [directory,'r',ea_stripex(options.prefs.rest),'_',options.prefs.prenii_unnormalized],...
    [],1,[],1);

% segmented anat images registered to mean rest image
for i=1:3
    ea_apply_coregistration([directory,'mean',options.prefs.rest], ...
        [directory,'c',num2str(i),options.prefs.prenii_unnormalized], ...
        [directory,'r',ea_stripex(options.prefs.rest),'_c',num2str(i),options.prefs.prenii_unnormalized], ...
        transform{1}, 'linear');
end

% Fix transformation names, replace 'mean' by 'r'
cellfun(@(f) movefile(f, strrep(f, 'mean', 'r')), transform);


function ea_smooth_fmri(signallength,options)
directory=[options.root,options.patientname,filesep];
filetimepts = ea_appendVolNum([directory,'r',options.prefs.rest], 1:signallength);

matlabbatch{1}.spm.spatial.smooth.data = filetimepts;
matlabbatch{1}.spm.spatial.smooth.fwhm = [6 6 6];
matlabbatch{1}.spm.spatial.smooth.dtype = 0;
matlabbatch{1}.spm.spatial.smooth.im = 0;
matlabbatch{1}.spm.spatial.smooth.prefix = 's';
jobs{1}=matlabbatch;
spm_jobman('run',jobs);
clear jobs matlabbatch

