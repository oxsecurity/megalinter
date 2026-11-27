import { Component, OnInit } from '@angular/core';

// Same deliberate failure as ../../.wireit/poison.component.ts, nested one level down: --exclude receives
// the directory name and onpush-census must skip it at any depth.
@Component({
  selector: 'app-poison-nested',
  template: `<p>{{ status }}</p>`,
})
export class PoisonNestedComponent implements OnInit {
  status = 'loading';

  ngOnInit(): void {
    setTimeout(() => {
      this.status = 'done';
    }, 1000);
  }
}
