function ea_checkforwardinv(options,forwardinv)
%
%
% USAGE:
%
%    ea_checkforwardinv(options,forwardinv)
%
% INPUTS:
%    options:
%    forwardinv:
%
% .. AUTHOR:
%       - Andreas Horn, Original file
%       - Ningfei Li, Original file
%       - Daniel Duarte, Documentation

switch forwardinv
    case 'forward'
        V=spm_vol([options.root,options.patientname,filesep,'y_ea_normparams.nii']);
        [~,template]=ea_whichnormmethod([options.root,options.patientname,filesep]);
        Vmni=spm_vol(template);
        
        if ~isequal(V.dim,Vmni(1).dim)
            
            ea_redo_inv([options.root,options.patientname,filesep],options,'forward');
        end
    case 'inverse'
        V=spm_vol([options.root,options.patientname,filesep,'y_ea_inv_normparams.nii']);
        Vanat=spm_vol([options.root,options.patientname,filesep,options.prefs.prenii_unnormalized]);
        if ~isequal(V.dim,Vanat.dim)
            ea_redo_inv([options.root,options.patientname,filesep],options,'inverse');
        end
end