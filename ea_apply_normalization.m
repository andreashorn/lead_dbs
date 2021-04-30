function ea_apply_normalization(options)
% Wrapper to apply normalization to the unnormalized files.
%
% USAGE:
%
%    ea_apply_normalization(options)
%
% INPUT:
%    options:
%
% .. AUTHOR:
%       - Andreas Horn, Original file
%       - Daniel Duarte, Documentation

directory=[options.root,options.patientname,filesep];
whichnormmethod=ea_whichnormmethod(directory);

switch whichnormmethod

    case ea_getantsnormfuns

        ea_ants_apply_transforms(options);

    case ea_getfslnormfuns

        ea_fsl_apply_normalization(options);

    case 'ea_normalize_suit'

        ea_spm_apply_normalization(options,'suit');

    otherwise % all SPM functions
        ea_spm_apply_normalization(options);
end
