import { Component, OnInit } from '@angular/core';

// A field the template reads is written when a promise resolves and nothing marks the view: under
// OnPush the list stays empty.
@Component({
  selector: 'app-stale-list',
  template: `
    <ul>
      @for (item of items; track item) {
        <li>{{ item }}</li>
      }
    </ul>
  `,
})
export class StaleListComponent implements OnInit {
  items: string[] = [];

  ngOnInit(): void {
    Promise.resolve(['first', 'second']).then((items) => {
      this.items = items;
    });
  }
}
