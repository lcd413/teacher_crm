from stark.service import v1
from crm import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import redirect,HttpResponse,render
from crm.congfigs.student import StudentConfig
from crm.congfigs.customer import CustomerConfig

class DeparmentConfig(v1.StarkConfig):
    list_display = ['title','code']

    # def get_list_display(self):
    #     result = []
    #     result.extend(self.list_display)
    #     result.append(v1.StarkConfig.edit)
    #     result.append(v1.StarkConfig.delete)
    #     result.insert(0,v1.StarkConfig.checkbox)
    #     return result

    edit_link = ['title',]

v1.site.register(models.Department,DeparmentConfig)



class UserInfoConfig(v1.StarkConfig):
    list_display = ['name','username','email','depart']
    edit_link = ['name']
    comb_filter = [
        v1.FilterOption('depart',text_func_name=lambda x: str(x),val_func_name=lambda x: x.code,)

    ]

    search_fields = ['name__contains','email__contains']
    show_search_form = True
    show_comb_filter = True




v1.site.register(models.UserInfo,UserInfoConfig)


class CourseConfig(v1.StarkConfig):
    list_display = ['name']
    edit_link = ['name',]
v1.site.register(models.Course,CourseConfig)


class SchoolConfig(v1.StarkConfig):
    list_display = ['title']
    edit_link = ['title',]
v1.site.register(models.School,SchoolConfig)


class ClassListConfig(v1.StarkConfig):

    def course_semester(self,obj=None,is_header=False):
        if is_header:
            return '班级'

        return "%s(%s期)" %(obj.course.name,obj.semester,)

    def num(self,obj=None,is_header=False):
        if is_header:
            return '人数'
        return 666
    def display_teachers(self, obj=None, is_header=False):
        if is_header:
            return '任课老师'

        html = []
        teacher_list = obj.teachers.all()
        for teacher in teacher_list:
            html.append(teacher.name)

        return ",".join(html)
    comb_filter = [
        v1.FilterOption('school', ),
        v1.FilterOption('course', )
    ]

    list_display = ['school','course','semester','price','start_date','graduate_date','memo',display_teachers,course_semester,num,'tutor']
    edit_link = [course_semester,]



v1.site.register(models.ClassList,ClassListConfig)


v1.site.register(models.Customer,CustomerConfig)



class ConsultRecordConfig(v1.StarkConfig):
    list_display = ['customer', 'consultant', 'date', 'note']
    comb_filter = [
        v1.FilterOption('customer')
    ]

    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 6
        ct = models.Customer.objects.filter(consultant=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse('别抢客户呀...')

        return super(ConsultRecordConfig,self).changelist_view(request,*args,**kwargs)

v1.site.register(models.ConsultRecord,ConsultRecordConfig)


#  上课记录


class PaymentRecordConfig(v1.StarkConfig):
    list_display = ['customer','class_list','pay_type','paid_fee','turnover','quote','note','date','consultant']

v1.site.register(models.PaymentRecord,PaymentRecordConfig)





v1.site.register(models.Student,StudentConfig)

# 上课记录
class CourseRecordConfig(v1.StarkConfig):
    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        url_list = [
            url(r'^(\d+)/score_list/$', self.wrap(self.score_list), name="%s_%s_score_list" % app_model_name),
        ]
        return url_list
    def score_list(self,request,record_id):
        if request.method == "GET":
            # 方式一
            # study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            # score_choices = models.StudyRecord.score_choices
            # return render(request,'score_list.html',{'study_record_list':study_record_list,'score_choices':score_choices})
            # 方式二
            from django.forms import Form
            from django.forms import fields
            from django.forms import widgets

            # class TempForm(Form):
            #     score = fields.ChoiceField(choices=models.StudyRecord.score_choices)
            #     homework_note = fields.CharField(widget=widgets.Textarea())
            data = []
            study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            for obj in study_record_list:
                # obj是对象
                TempForm = type('TempForm', (Form,), {
                    'score_%s' % obj.pk: fields.ChoiceField(choices=models.StudyRecord.score_choices),
                    'homework_note_%s' % obj.pk: fields.CharField(widget=widgets.Textarea())
                })
                data.append({'obj': obj, 'form': TempForm(
                    initial={'score_%s' % obj.pk: obj.score, 'homework_note_%s' % obj.pk: obj.homework_note})})
            return render(request, 'score_list.html',
                          {'data': data})
        else:
            data_dict = {}
            for key, value in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name, nid = key.rsplit('_', 1)
                if nid in data_dict:
                    data_dict[nid][name] = value
                else:
                    data_dict[nid] = {name: value}

            for nid, update_dict in data_dict.items():
                models.StudyRecord.objects.filter(id=nid).update(**update_dict)

            return redirect(request.path_info)
        # # 这一天上课的所有学生的学习记录
        # study_record_list=models.StudyRecord.objects.filter(course_record=record_id)

    def display_score_list(self, obj=None, is_header=False):
        if is_header:
            return '成绩录入'
        from django.urls import reverse
        rurl = reverse("stark:crm_courserecord_score_list", args=(obj.pk,))
        return mark_safe("<a href='%s'>成绩录入</a>" % rurl)
    show_actions = True
    def attendance(self,obj=None,is_header=False):
        if is_header:
            return "考勤"
        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>考勤管理</a>"%obj.pk)


    def multi_del(self, request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        return redirect("/stark/crm/courserecord/")

    multi_del.short_desc = "批量删除"

    def multi_init(self, request):
        # 上课记录的id
        pk_list = request.POST.getlist('pk')
        # print(pk_list)
        # 上课记录的对象
        record_list=models.CourseRecord.objects.filter(id__in=pk_list)
        # print(record_list)
        # 循环每一条上课记录（day1，day2）
        for record in record_list:
            exists=models.StudyRecord.objects.filter(course_record=record).exists()
            if exists:
                continue

            # record.class_obj(关联的班级)
            # 学生列表
            student_list = models.Student.objects.filter(class_list=record.class_obj)
            bulk_list = []
            for student in student_list:
                # 为每一个学生创建dayn的学习记录
                bulk_list.append(models.StudyRecord(student=student, course_record=record))
            models.StudyRecord.objects.bulk_create(bulk_list)





    multi_init.short_desc = "学生初始化"
    actions = [multi_del, multi_init]
    list_display = ['class_obj','day_num','teacher','date','course_title','course_memo','has_homework','homework_title','homework_memo','exam',attendance,display_score_list]
v1.site.register(models.CourseRecord,CourseRecordConfig)

class StudyRecordConfig(v1.StarkConfig):
    show_add_btn = False
    def display_record(self,obj=None,is_header=False):
        if is_header:
            return '出勤'
        return obj.get_record_display()
    # 学生学习记录
    comb_filter = [
        v1.FilterOption('course_record')
    ]
    def action_checked(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='checked')
    action_checked.short_desc= "签到"
    def action_vacate(self,request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='vacate')
    action_vacate.short_desc= "请假"
    def action_late(self,request):
        pk_list=request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='late')
    action_late.short_desc= "迟到"
    def action_noshow(self,request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='noshow')
    action_noshow.short_desc= "缺勤"
    def action_leave_early(self,request):
        pk_list = request.POST.getlist("pk")
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='leave_early')
    action_leave_early.short_desc= "早退"
    show_actions = True
    actions = [action_checked, action_vacate, action_late, action_noshow, action_leave_early]

    list_display = ['course_record','student','record','score','homework_note','note','homework','stu_memo','date',display_record]
v1.site.register(models.StudyRecord,StudyRecordConfig)
