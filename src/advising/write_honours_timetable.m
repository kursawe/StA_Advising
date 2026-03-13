function write_honours_timetable(file_1,year,output_file)
%write_honours_timetable 
%   Given the module catalogue file and starting year, make timetables for
%   the next three academic years and export to excel
arguments
    file_1 string = 'Module_catalogue.xlsx' 
    year string = '2026_27' % or 2027_28 % may need adjustments year to year
    output_file string = 'output-timetable.xlsx' 
end

year=year{1};

M = load_MC_honours(file_1);
M.Properties.VariableNames{9}='Division';
writetable(M(:,[1,2,4,10,9,5:8]),output_file,'Sheet','Catalogue')

semester='S1'; make_timetable_instance(M,semester,year);
semester='S2'; make_timetable_instance(M,semester,year);

year = strcat(year(1:2),num2str(str2double(year(3:4))+1),year(5),num2str(str2double(year(6:7))+1));
semester='S1'; make_timetable_instance(M,semester,year);
semester='S2'; make_timetable_instance(M,semester,year);

year = strcat(year(1:2),num2str(str2double(year(3:4))+1),year(5),num2str(str2double(year(6:7))+1));
semester='S1'; make_timetable_instance(M,semester,year);
semester='S2'; make_timetable_instance(M,semester,year);

    function make_timetable_instance(M,semester,year)
        [T_odd,T_even,T_other]= make_honours_timetable(M,semester,year);
        writetable(T_odd,output_file,'Sheet',strcat(semester,'_',year),'Range','A1')
        writetable(T_even,output_file,'Sheet',strcat(semester,'_',year),'Range','E1')
        writetable(T_other,output_file,'Sheet',strcat(semester,'_',year),'Range','I1')
    end


end