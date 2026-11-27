import { Component, OnInit } from '@angular/core';

// A field the template reads is written in a timer callback and nothing marks the view: under OnPush
// the paragraph keeps showing "loading".
@Component({
  selector: 'app-blocked',
  template: `<p>{{ status }}</p>`,
})
export class BlockedComponent implements OnInit {
  status = 'loading';

  ngOnInit(): void {
    setTimeout(() => {
      this.status = 'done';
    }, 1000);
  }
}
