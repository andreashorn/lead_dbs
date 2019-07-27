function ea_checkspm
% 
%
% USAGE:
%
%    ea_checkspm
%
% .. AUTHOR:
%       - Andreas Horn, Original file
%       - Ningfei Li, Original file
%       - Daniel Duarte, Documentation

if ~isdeployed
    try
        ver=spm('version');
    catch
        ea_error('SPM seems not installed. Please install SPM12 and add it to the Matlab path before using Lead-DBS.');
    end
    
    if ~any(ismember(ver(8:11),'.')) % old version format
        if str2double(ver(8:11))<6906
            msgbox('Some functions (such as SPM SHOOT and DARTEL) may not be available using your SPM version. Please upgrade SPM12 to at least revision 6906 (or simply update to newest release).');
        end
    end
end