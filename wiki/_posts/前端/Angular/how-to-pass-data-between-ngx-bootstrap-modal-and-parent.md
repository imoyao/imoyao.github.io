---
title: Angular 弹框与父组件之间传值的问题（最重要的是父组件接收子组件的返回值）
toc: true
date: 2020-05-25 18:21:46
tags:
- 前端
---
## 子组件（弹框 modal）中

```typescript
@Output() action = new EventEmitter();

// now on click ok button emit the output from confirmPopupComponent
public clickOk() {
    this.loading = true;
    this.action.emit(true); // 提交给父组件，here you can send object  instead of true
}
```
## 父组件中，调用发起方

```typescript
LocateDiskAction(lightState) {
    this.clickModal = true  // 弹框置true
    let lightDisk = await this.getDisklight(lightState)
    let initialState = {
      lightDisk: lightDisk,
      action: lightState,
      hostName: this.hostName,
    };
    let bsModalRef = this.modalService.show(DiskLocateModalComponent, {
      initialState,
    });
    bsModalRef.content.action.take(1).subscribe((value) => {
        console.log(value) // here you will get the value
    });
    }
```
如果上面的调用出错，可以试试下面的方法：
```typescript
openModalWithComponent() {
  const initialState = {
    list: [
      {"tag":'Count',"value":this.itemList.length}
    ]
  };
  this.bsModalRef = this.modalService.show(ItemAddComponent, {initialState});
  this.bsModalRef.content.closeBtnName = 'Close';

  this.bsModalRef.content.event.subscribe(res => {
    this.itemList.push(res.data);
  });
}
```

## 同步调用

```typescript
  async LocateDiskAction(lightState) {
    this.clickModal = true  // 弹框置true
    let lightDisk = await this.getDisklight(lightState)
    let initialState = {
      lightDisk: lightDisk,
      action: lightState,
      hostName: this.hostName,
    };

    let bsModalRef = this.modalService.show(DiskLocateModalComponent, {
      initialState,
    });

    let newSubscriber = this.modalService.onHide.subscribe(r=>{
      newSubscriber.unsubscribe();
      this.clickModal = false
      console.log('DATA',bsModalRef.content);
    });
  }

  getDisklight(diskSignal) {
    return this.client.get(`api/disk/${this.hostName}?disk_status=${diskSignal}`).toPromise();
  }
```
## 参考链接

1. [How to pass data to modal ngx-bootstrap and receive return data ? · Issue #2290 · valor-software/ngx-bootstrap](https://github.com/valor-software/ngx-bootstrap/issues/2290)
2. [How to pass data between NGX Bootstrap modal and parent](https://medium.com/@randulakoralage82/how-to-pass-data-between-ngx-bootstrap-modal-and-parent-e348cd596cf7)