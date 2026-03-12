function test_catalogue_differences(file_1,file_2,N_cols)
%test_catalogue_differences 
%   Compares two versions of the module catalogue with filenames file_1 and
%   file_2.
%   Prints to screen logs of modules that either are found in one file but
%   not the other (and vice versa), or where a module appears in both files, but the details are changed. 

arguments
    file_1 string % New file (give a new name for testing purposes)
    file_2 string = 'Module_catalogue.xlsx' % previous file
    N_cols double = 8 %truncate file table after the first N_cols
end


opts=detectImportOptions(file_1,"TextType","string");
opts = setvaropts(opts,opts.VariableNames,"FillValue","");
MC1 = readtable(file_1, opts);
MC2 = readtable(file_2, opts);

MC1=MC1(:,1:N_cols);
MC2=MC2(:,1:N_cols);

format compact

disp(['File 1: ',file_1])
disp(['File 2: ',file_2])
disp('Detect and display file differences')
disp(" ")

N=numel(MC1(:,1));
for I=1:N
    module_code=MC1.ModuleCode(I);
%    II=find(MC1.ModuleCode==module_code); % copes with modules listed twice in file 2
    J=find(MC2.ModuleCode==module_code);
    if isempty(J)
        disp(strcat("Module Code: ",module_code))
        disp("Module exists in file 1 but does not exist in file 2")
        disp(" ")    
    end
end

N=numel(MC2(:,1));
for I=1:N
    module_code=MC2.ModuleCode(I);
    II=find(MC2.ModuleCode==module_code); % copes with modules listed twice in file 2
    J=find(MC1.ModuleCode==module_code);
    if isempty(J)
        disp(strcat("Module Code: ",module_code))
        disp("Module exists in file 2 but does not exist in file 1")
        disp(" ")

    else
        test=isequal(MC1(J,:),MC2(II,:));
        if test
           % disp(["Module Code: ",module_code," data matches between file 1 and file 2"])
        else
            disp(strcat("Module Code: ",module_code))
            disp("Data does not match between file 1 and file 2")
            row_file_1=MC1(J,3:end);
            row_file_2=MC2(I,3:end);
            disp(row_file_1)
            disp(row_file_2)
            disp(" ")
        end
    end

end


end