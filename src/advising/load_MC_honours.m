function M = load_MC_honours(file_1)
arguments
    file_1 string = 'Module_catalogue.xlsx'
end

opts=detectImportOptions(file_1,"TextType","string");
opts = setvaropts(opts,opts.VariableNames,"FillValue","");
MC1 = readtable(file_1, opts);

N=numel(MC1(:,1));
test_honours=logical(zeros(N,1));
for I=1:N
    module_code=MC1.ModuleCode{I};
    test_honours(I)=(str2double(module_code(3))>=3)&&(strcmpi(module_code(1:2),'MT'));
end
M=MC1(test_honours,:);
M=clean_timetable(M);

    function M=clean_timetable(M) % warning, may fail if multiple modules are found
        ind_clean=find(M.Timetable=="12noon Mon (odd weeks), Wed, Fri, 1pm Fri");
        disp(['Module code: ',M.ModuleCode{ind_clean},' had its timetable cleaned (removed afternoon classes)'])
        M.Timetable(ind_clean)="12noon Mon (odd weeks), Wed, Fri";
        ind_clean=find(M.Timetable=="12noon Mon (odd weeks), Wed, Fri, 2pm Fri");
        disp(['Module code: ',M.ModuleCode{ind_clean},' had its timetable cleaned (removed afternoon classes)'])
        M.Timetable(ind_clean)="12noon Mon (odd weeks), Wed, Fri";
    end

end

