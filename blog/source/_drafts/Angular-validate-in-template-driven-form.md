---
title: 如何禁用 Angular 中模板驱动表单中的某个字段？
date: 2020-03-09 18:22:25
tags:
- form
- Angular
- 前端
hide: true
categories:
- 工作日常
cover: /images/logos/angular.svg
---
## 前言
书接上回，我们在[上文](/blog/2020-03-06/Angular-orderBy-Object-or-Array/)中将表单展示出来了，但是怎么按照逻辑对表单进行限制呢？比如说基本的禁用表单中的某个字段？
## 错误

### There is no directive with “exportAs” set to “ngModel” in Angular
参见[typescript - There is no directive with "exportAs" set to "ngModel" in Angular - Stack Overflow](https://stackoverflow.com/questions/49130718/there-is-no-directive-with-exportas-set-to-ngmodel-in-angular)
```plain
<!--    password-->
          <div class="col-sm-7" *ngIf="['pw', 'npw'].includes(moduleOption.value.type)">
            <div class="input-group">
              <input class="form-control"
                     type="password"
                     placeholder="Password..."
                     id="{{ moduleOption.value.name }}"
                     #password="ngModel" # 删除此行的绑定
                     formControlName="{{ moduleOption.value.name }}">
              <span class="input-group-btn">
                <button type="button"
                        class="btn btn-default"
                        cdPasswordButton="{{ moduleOption.value.name }}">
                </button>
              </span>
            </div>
            <span class="help-block"
                  *ngIf="ipmiModuleForm.showError(moduleOption.value.name, frm, 'required')"
                  i18n>This field is required.</span>
          </div>

          <div class="col-sm-7" *ngIf="moduleOption.value.type === 'rpw'">
            <div class="input-group">
              <input class="form-control"
                     type="password"
                     placeholder="Confirm password..."
                     [RepeatPassword]="password"
                     id="{{ moduleOption.value.name }}"
                     formControlName="{{ moduleOption.value.name }}">
              <span class="input-group-btn">
                <button type="button"
                        class="btn btn-default"
                        cdPasswordButton="{{ moduleOption.value.name }}">
                </button>
              </span>
            </div>
            <span class="help-block"
                  *ngIf="ipmiModuleForm.showError(moduleOption.value.name, frm, 'required') || needRePw"
                  i18n>This field is required.</span>
            <span class="help-block"
                  *ngIf="ipmiModuleForm.showError(moduleOption.value.name, frm, 'match') || notEqual"
                  i18n>Password confirmation doesn't match the password.</span>
          </div>
```
> On one hand, you use reactive API linking this control to the explicitly created model property from your TS code: formControlName="pacName". On the other, you're trying to bind to the never-created implicit model from the template-driven API: #name="ngModel" and name="name".

一方面，您使用反应式（reactive）API 将此控件链接到您的 TS 代码中的显式创建的模型属性：formControlName =“xxxx”。另一方面，尝试通过模板驱动的 API 绑定到从未创建的隐式模型。写的代码自相矛盾了，删除其中一种绑定方法即可。
