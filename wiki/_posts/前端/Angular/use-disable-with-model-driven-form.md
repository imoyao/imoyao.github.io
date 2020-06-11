---
title: Angular 中如何对一个动态表单根据 select 的选项 disable 关联的 input？
toc: true
date: 2020-06-11 17:21:46
tags:
- 前端
- Angular
---
## 代码
基本思路是使用`statusChanges`监测 form 的 select 控件值，当值发生变化时，对关联值调用`disable()`方法使能或禁用。
```plain
createForm() {
    const controlsConfig = {};
    _.forEach(this.moduleOptions, (moduleOption) => {
      controlsConfig[moduleOption.name] = [
        moduleOption.default_value,
        this.getValidators(moduleOption),
      ];
    });
    this.ipmiModuleForm = this.formBuilder.group(controlsConfig);
    // see also:
    // 1. https://stackoverflow.com/questions/39681674/use-disable-with-model-driven-form
    // 2. https://stackoverflow.com/questions/45412773/how-to-disable-all-formcontrols-inside-a-formgroup
    let modelControl = this.ipmiModuleForm.get('model')
    let ipControl = this.ipmiModuleForm.get('ip_addr')
    let maskControl = this.ipmiModuleForm.get('netmask')
    let gwControl = this.ipmiModuleForm.get('gateway')

    modelControl.statusChanges.subscribe((newStatus) => {
    if (modelControl.value !='dhcp') {
      // 如果网络模式改为dhcp，则配置项全disable,否则enable
      ipControl.enable();
      maskControl.enable();
      gwControl.enable();
    } else {
      ipControl.disable();
      maskControl.disable();
      gwControl.disable();
    }
  });
  }
```

## 效果
![关联禁用输入框](/pics/form-disable.gif)

## 参考链接
1. [angular - Use disable with model-driven form - Stack Overflow](https://stackoverflow.com/questions/39681674/use-disable-with-model-driven-form)
2. [angular - Disable Input fields in reactive form - Stack Overflow](https://stackoverflow.com/questions/42840136/disable-input-fields-in-reactive-form)
3. [angular - How to disable all FormControls inside a FormGroup - Stack Overflow](https://stackoverflow.com/questions/45412773/how-to-disable-all-formcontrols-inside-a-formgroup)