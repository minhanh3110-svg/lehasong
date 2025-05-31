from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Sample, TestResult, EnvironmentLog
from ..forms import SampleForm, TestResultForm, EnvironmentLogForm
from .. import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('main/index.html', title='Trang chủ')

@main.route('/samples')
@login_required
def samples():
    page = request.args.get('page', 1, type=int)
    samples = Sample.query.order_by(Sample.received_date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('main/samples.html', title='Quản lý mẫu', samples=samples)

@main.route('/sample/new', methods=['GET', 'POST'])
@login_required
def new_sample():
    form = SampleForm()
    if form.validate_on_submit():
        sample = Sample(
            code=form.code.data,
            name=form.name.data,
            type=form.type.data,
            notes=form.notes.data,
            submitter=current_user
        )
        db.session.add(sample)
        db.session.commit()
        flash('Mẫu mới đã được tạo thành công!', 'success')
        return redirect(url_for('main.samples'))
    return render_template('main/sample_form.html', title='Tạo mẫu mới', form=form)

@main.route('/sample/<int:id>')
@login_required
def view_sample(id):
    sample = Sample.query.get_or_404(id)
    return render_template('main/sample_detail.html', title='Chi tiết mẫu', sample=sample)

@main.route('/sample/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sample(id):
    sample = Sample.query.get_or_404(id)
    form = SampleForm(obj=sample)
    if form.validate_on_submit():
        sample.code = form.code.data
        sample.name = form.name.data
        sample.type = form.type.data
        sample.notes = form.notes.data
        db.session.commit()
        flash('Thông tin mẫu đã được cập nhật!', 'success')
        return redirect(url_for('main.view_sample', id=sample.id))
    return render_template('main/sample_form.html', title='Sửa thông tin mẫu', form=form)

@main.route('/sample/<int:id>/result/new', methods=['GET', 'POST'])
@login_required
def new_result(id):
    sample = Sample.query.get_or_404(id)
    form = TestResultForm()
    if form.validate_on_submit():
        result = TestResult(
            test_name=form.test_name.data,
            result_value=form.result_value.data,
            status=form.status.data,
            notes=form.notes.data,
            sample=sample
        )
        if form.status.data == 'completed':
            sample.status = 'completed'
            sample.completed_date = datetime.utcnow()
        db.session.add(result)
        db.session.commit()
        flash('Kết quả xét nghiệm đã được thêm!', 'success')
        return redirect(url_for('main.view_sample', id=sample.id))
    return render_template('main/result_form.html', title='Thêm kết quả', form=form, sample=sample)

@main.route('/environment')
@login_required
def environment():
    page = request.args.get('page', 1, type=int)
    logs = EnvironmentLog.query.order_by(EnvironmentLog.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('main/environment.html', title='Môi trường', logs=logs)

@main.route('/environment/log', methods=['GET', 'POST'])
@login_required
def log_environment():
    form = EnvironmentLogForm()
    if form.validate_on_submit():
        log = EnvironmentLog(
            temperature=form.temperature.data,
            humidity=form.humidity.data,
            location=form.location.data,
            notes=form.notes.data
        )
        db.session.add(log)
        db.session.commit()
        flash('Thông số môi trường đã được ghi lại!', 'success')
        return redirect(url_for('main.environment'))
    return render_template('main/environment_form.html', title='Ghi thông số môi trường', form=form) 