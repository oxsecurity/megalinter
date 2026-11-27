import { Component } from '@angular/core';

// A plain field is fine as long as it only changes inside an event handler of the component.
@Component({
  selector: 'app-toggle',
  template: `<button (click)="open = !open">{{ open ? 'Hide' : 'Show' }}</button>`,
})
export class ToggleComponent {
  open = false;
}
