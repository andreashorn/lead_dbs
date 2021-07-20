function ea_magetcheck_norm_peers(options,peerfolders)
% Function that checks maget peers for normalization with an ANTs function
% and does normalize them if not done before.
%
% USAGE:
%
%    ea_magetcheck_norm_peers(options,peerfolders)
%
% INPUTS:
%    options:
%    peerfolder:

for peer=1:length(peerfolders)
    poptions=options;
    [poptions.root,poptions.patientname]=fileparts(peerfolders{peer});
    poptions.root=[poptions.root,filesep];
    poptions=ea_assignpretra(poptions);
    % make sure peer has been normalized using ANTs
    if ~ismember(ea_whichnormmethod([peerfolders{peer},filesep]),ea_getantsnormfuns)
        ea_dumpnormmethod(poptions,'ea_normalize_ants_multimodal','normmethod');
        ea_normalize_ants(poptions)
    else
        % make sure peer's anatomy files have been coregistered.
        if ~ea_seemscoregistered(poptions)
            ea_coreg_all_mri(poptions,0);
        end
    end
end