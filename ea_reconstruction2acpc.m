function ea_reconstruction2acpc(options)

directory=[options.root,options.patientname,filesep];
load([directory,filesep,'ea_reconstruction.mat']);

    for side=1:length(options.sides)
        for c=1:size(reco.native.coords_mm{side}(:,1),1);
            cfg.xmm=reco.native.coords_mm{side}(c,1);
            cfg.ymm=reco.native.coords_mm{side}(c,2);
            cfg.zmm=reco.native.coords_mm{side}(c,3);
            cfg.acmcpc=2; % map to AC
            fid=ea_native2acpc(cfg,{directory});
            
            reco.acpc.coords_mm{side}(c,:)=fid.WarpedPointACPC;
        end
    end
    
    
    save([directory,filesep,'ea_reconstruction.mat'],'reco');
    

