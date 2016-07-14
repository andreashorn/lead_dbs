function nii=ea_load_nii(fname, mode)
% simple nifti reader using SPM.

% try to combine ea_load_nii and load_nii_proxi here, temporarily solution
% will have a unified interface for nii/nii.gz reading in the future
% by default, use the original ea_load_nii way
% if mode=='simple', use the load_nii_proxi way
if nargin < 2
    mode = 0; 
end

if strcmp(fname(end-2:end),'.gz')
    wasgzip=1;
    gunzip(fname);
    fname=fname(1:end-3);
else
    wasgzip=0;
end

if mode
    V=spm_vol(fname);
    X=spm_read_vols(V);
    nii.img=X;
    nii.hdr=V;
else
    nii=spm_vol(fname);
    img=spm_read_vols(nii);
    if length(nii)>1 % multi volume;
       for n=1:length(nii)
          nii(n).img=squeeze(img(:,:,:,n));
       end
    else
        nii.img=img;
    end
    try
        nii.hdr.dime.pixdim=nii.mat(logical(eye(4)));
    end
end

if wasgzip
    delete(fname); % since gunzip makes a copy of the zipped file.
end