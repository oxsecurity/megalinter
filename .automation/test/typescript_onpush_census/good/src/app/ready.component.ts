import { Component, input, signal } from '@angular/core';

// Every change the template can show arrives through an OnPush trigger: an input or a signal.
@Component({
  selector: 'app-ready',
  template: `<p>{{ label() }}: {{ count() }}</p><button (click)="add()">Add</button>`,
})
export class ReadyComponent {
  readonly label = input('Clicks');
  readonly count = signal(0);

  add(): void {
    this.count.update((n) => n + 1);
  }
}
