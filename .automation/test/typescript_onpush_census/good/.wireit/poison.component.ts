import { Component, OnInit } from '@angular/core';

// This component deliberately fails onpush-census: a field the template reads is written in a timer
// callback. It sits inside .wireit, a default excluded directory: the project lint mode success test
// passes only if excluded directories are forwarded to onpush-census through --exclude.
@Component({
  selector: 'app-poison',
  template: `<p>{{ status }}</p>`,
})
export class PoisonComponent implements OnInit {
  status = 'loading';

  ngOnInit(): void {
    setTimeout(() => {
      this.status = 'done';
    }, 1000);
  }
}
