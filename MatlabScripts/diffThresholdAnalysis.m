clear; clc;



while true
    A = importdata('diff.txt');

    a = 1;
    b = [1/4 1/4 1/4 1/4];
    
    filtered = filter(b,a,A);
    
    for n = 1:length(A)
        meanTable(n) = mean(A(1:n));
        standardDev(n) = std(A(1:n));
    end

    for n = 1:length(filtered)
        filteredMeanTable(n) = mean(filtered(1:n));
        filteredStandardDev(n) = std(filtered(1:n));
    end


    figure(1)
    legend('diff', 'threshold', 'mean')
    plot(A)
    hold on
    plot(meanTable+(3*standardDev))
    plot(meanTable)
    %plot(meanTable-(3*standardDev))
    hold off
    
    figure(2)
    legend('diff', 'threshold', 'mean')
    plot(filtered)
    hold on
    plot(filteredMeanTable+(3*filteredStandardDev))
    plot(filteredMeanTable)
    %plot(meanTable-(3*standardDev))
    hold off
    
    pause(0.1)
end