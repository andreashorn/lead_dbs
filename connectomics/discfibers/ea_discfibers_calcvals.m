function [fibsvalBin, fibsvalSum, fibsvalMean, fibsvalPeak, fibsval5Peak] = ea_discfibers_calcvals(vats, cfile)
% Calculate fiber connection values based on the VATs and the connectome

disp('Load Connectome...');
load(cfile, 'fibers', 'idx');

prefs = ea_prefs;
thresh = prefs.machine.vatsettings.horn_ethresh*1000;

[numPatient, numSide] = size(vats);

fibsvalBin = cell(1, numSide);
fibsvalSum = cell(1, numSide);
fibsvalMean = cell(1, numSide);
fibsvalPeak = cell(1, numSide);
fibsval5Peak = cell(1, numSide);

for side = 1:numSide
    fibsvalBin{side} = zeros(length(idx), numPatient);
    fibsvalSum{side} = zeros(length(idx), numPatient);
    fibsvalMean{side} = zeros(length(idx), numPatient);
    fibsvalPeak{side} = zeros(length(idx), numPatient);
    fibsval5Peak{side} = zeros(length(idx), numPatient);

    disp(['Calculate for side ', num2str(side), ':']);
    for pt = 1:numPatient
        disp(['VAT ', num2str(pt, ['%0',num2str(numel(num2str(numPatient))),'d']), '/', num2str(numPatient), '...']);
        vat = vats{pt,side};

        % Threshold the vat efield
        vatInd = find(vat.img(:)>thresh);

        % Trim connectome fibers
        [xvox, yvox, zvox] = ind2sub(size(vat.img), vatInd);
        vatmm = ea_vox2mm([xvox, yvox, zvox], vat.mat);
        filter = all(fibers(:,1:3)>=min(vatmm),2) & all(fibers(:,1:3)<=max(vatmm), 2);
        trimmedFiber = fibers(filter,:);

        % Map mm connectome fibers into VAT voxel space
        [trimmedFiberInd, ~, trimmedFiberID] = unique(trimmedFiber(:,4), 'stable');
        fibVoxInd = splitapply(@(fib) {ea_mm2uniqueVoxInd(fib, vat)}, trimmedFiber(:,1:3), trimmedFiberID);

        % Remove outliers
        fibVoxInd(cellfun(@(x) any(isnan(x)), fibVoxInd)) = [];
        trimmedFiberInd(cellfun(@(x) any(isnan(x)), fibVoxInd)) = [];

        % Find connected fibers
        connected = cellfun(@(fib) any(ismember(fib, vatInd)), fibVoxInd);

        % Generate binary fibsval for the T-test method
        fibsvalBin{side}(trimmedFiberInd(connected), pt)=1;

        % Checck intersection between vat and the connected fibers
        vals = cellfun(@(fib) vat.img(intersect(fib, vatInd)), fibVoxInd(connected), 'Uni', 0);

        % Generate fibsval for the Spearman's correlation method
        fibsvalSum{side}(trimmedFiberInd(connected), pt) = cellfun(@sum, vals);
        fibsvalMean{side}(trimmedFiberInd(connected), pt) = cellfun(@mean, vals);
        fibsvalPeak{side}(trimmedFiberInd(connected), pt) = cellfun(@max, vals);
        fibsval5Peak{side}(trimmedFiberInd(connected), pt) = cellfun(@(x) mean(maxk(x,ceil(0.05*numel(x)))), vals);
    end

    % Convert to sparse matrix
    fibsvalBin{side} = sparse(fibsvalBin{side});
    fibsvalSum{side} = sparse(fibsvalSum{side});
    fibsvalMean{side} = sparse(fibsvalMean{side});
    fibsvalPeak{side} = sparse(fibsvalPeak{side});
    fibsval5Peak{side} = sparse(fibsval5Peak{side});
end