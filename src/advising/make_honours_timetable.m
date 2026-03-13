function [T_odd,T_even,T_other]= make_honours_timetable(M,semester,year)
arguments
    M table 
    semester string = 'S1'
    year string = '2026_27' % or 2027_28 % may need adjustments year to year
end

M=timetable_clarifications(M);
year=year{1};
if mod(str2double(year(1:4)),2)==0
    ind=find((M.Semester==semester)&((M.RunningStatus=="Runs every year")|(M.RunningStatus=="Alternates (2026/27)")));
else
    ind=find((M.Semester==semester)&((M.RunningStatus=="Runs every year")|(M.RunningStatus=="Alternates (2027/28)")));
end
M_test=M(ind,:);
T_odd=make_timetable(M_test,"odd");
T_even=make_timetable(M_test,"even");
T_other=make_other_timetable(M_test);
if strcmpi(semester,'S1')
    T_other=[T_other;M(M.ModuleCode=="MT5766",[5,1,2])];
end
    function T=make_timetable(M_test,parity)
        if strcmp(parity,"odd")
        ind_test=find(M_test.Timetable=="9am Mon (odd weeks), Wed, Fri");
        T=M_test(ind_test,[5,1,2]);
        ind_test=find(M_test.Timetable=="10am Mon (odd weeks), Wed, Fri");
        T=[T;M_test(ind_test,[5,1,2])];
        ind_test=find(M_test.Timetable=="11am Mon (odd weeks), Wed, Fri");
        T=[T;M_test(ind_test,[5,1,2])];
        ind_test=find(M_test.Timetable=="12noon Mon (odd weeks), Wed, Fri");
        T=[T;M_test(ind_test,[5,1,2])];
        else
        ind_test=find(M_test.Timetable=="9am Mon (even weeks), Tue, Thu");
        T=[M_test(ind_test,[5,1,2])];
        ind_test=find(M_test.Timetable=="10am Mon (even weeks), Tue, Thu");
        T=[T;M_test(ind_test,[5,1,2])];
        ind_test=find(M_test.Timetable=="11am Mon (even weeks), Tue, Thu");
        T=[T;M_test(ind_test,[5,1,2])];
        ind_test=find(M_test.Timetable=="12noon Mon (even weeks), Tue, Thu");
        T=[T;M_test(ind_test,[5,1,2])];
        end
       
    end

    function T=make_other_timetable(M_test)
        ind_test=find(M_test.Timetable~="9am Mon (odd weeks), Wed, Fri" ...
            & M_test.Timetable~="10am Mon (odd weeks), Wed, Fri" ...
            & M_test.Timetable~="11am Mon (odd weeks), Wed, Fri" ...
            & M_test.Timetable~="12noon Mon (odd weeks), Wed, Fri"...
            & M_test.Timetable~="9am Mon (even weeks), Tue, Thu" ...
            & M_test.Timetable~="10am Mon (even weeks), Tue, Thu" ...
            & M_test.Timetable~="11am Mon (even weeks), Tue, Thu" ...
            & M_test.Timetable~="12noon Mon (even weeks), Tue, Thu");
        T=M_test(ind_test,[5,1,2]);
    end

    function M=timetable_clarifications(M)
        ind_ISM=M.ModuleCode=="MT5590";
        if sum(ind_ISM)>=1
            M=M(~ind_ISM,:);
        end      
    end


end

