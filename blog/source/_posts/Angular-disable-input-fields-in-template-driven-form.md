---
title: 如何禁用 Angular 中模板驱动表单中的某个字段？
date: 2020-03-09 18:22:25
tags:
- form
- Angular
- 前端
categories:
- 工作日常
cover: /images/logos/angular.svg
subtitle: checkbox 的使用以及表单关联操作。
---
## 前言
书接上回，我们在[上文](/blog/2020-03-06/Angular-orderBy-Object-or-Array/)中将表单展示出来了，但是怎么按照逻辑对表单进行限制呢？比如说基本的禁用表单中的某个字段？
## 方法
直接使用`disable=true`并不能随着 checkbox 的变化使值变化，所以我们需要这么写：
```angular2html
<!--html-->
<!-- Field control -->
<!-- bool -->
<div class="form-group"
  *ngIf="moduleOption.value.type === 'bool'">
  <div class="checkbox checkbox-primary">
    <input id="{{ moduleOption.value.name }}"
           type="checkbox"
           (change)="onUserCheckMode()"
           formControlName="{{ moduleOption.value.name }}">
    <label i18n for="{{ moduleOption.value.name }}"> Check set mode auto/manual.</label>
  </div>
</div>
```
```angularjs
// xx.ts
//在选择time时，如果自动，则disable部分input
  onUserCheckMode() {
    this.isAuto = this.sysSettingForm.value.auto == true;
    if (this.isTime) {
      if (this.isAuto == true) {
        this.sysSettingForm.get('ntp_addr').enable();
        this.sysSettingForm.get('date').disable();
        this.sysSettingForm.get('time').disable();
        this.sysSettingForm.get('time_zone').disable();
      } else {
        this.sysSettingForm.get('ntp_addr').disable();
        this.sysSettingForm.get('date').enable();
        this.sysSettingForm.get('time').enable();
        this.sysSettingForm.get('time_zone').enable();
      }
    }
  }
  
  // 初始化表格时，对表格也需要disable
  createForm() {
    const controlsConfig = {};
    _.forEach(this.moduleOptions, (moduleOption) => {
      switch (moduleOption.type) {
        case 'bool':
          controlsConfig[moduleOption.name] = [this.isAuto, this.getValidators(moduleOption)];
          break;
        default:
          controlsConfig[moduleOption.name] = [moduleOption.default_value, this.getValidators(moduleOption)];

      }
    });
    this.sysSettingForm = this.formBuilder.group(controlsConfig);
    if (this.isTime) {
      if (this.isAuto == true) {
        this.sysSettingForm.get('ntp_addr').enable();
        this.sysSettingForm.get('date').disable();
        this.sysSettingForm.get('time').disable();
        this.sysSettingForm.get('time_zone').disable();
      } else {
        this.sysSettingForm.get('ntp_addr').disable();
        this.sysSettingForm.get('date').enable();
        this.sysSettingForm.get('time').enable();
        this.sysSettingForm.get('time_zone').enable();
      }
    }
  }
```
## 效果
![根据选择框disable/enable](/images/Angular-form-disable.gif)

## 参考
[angular - Disable Input fields in reactive form - Stack Overflow](https://stackoverflow.com/questions/42840136/disable-input-fields-in-reactive-form)