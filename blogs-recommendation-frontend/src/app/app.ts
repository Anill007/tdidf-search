import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, resource, signal } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgSelectComponent } from '@ng-select/ng-select';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [NgSelectComponent, FormsModule, ReactiveFormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private http = inject(HttpClient);
  protected searchQuery = signal(null);
  protected selectedBlog = signal<any>(null);

  private blogsResource = resource({
    loader: () => firstValueFrom(this.http.get<any[]>('http://127.0.0.1:5000/posts'))
  })
  protected blogsLoading = this.blogsResource.isLoading;
  protected blogsError = this.blogsResource.error;
  protected blogs = this.blogsResource.value;

  private suggestedBlogsResource = resource({
    params: () => {
      return { query: this.searchQuery() };
    },
    loader: (trigger) => {
      const query = trigger.params.query;
      if (!query) return Promise.resolve([]);
      return firstValueFrom(this.http.get<any[]>(`http://127.0.0.1:5000/search?query=${trigger.params.query}&&similarity=0.0`))
    }
  })
  protected suggestedBlogsLoading = this.suggestedBlogsResource.isLoading;
  protected suggestedBlogsError = this.suggestedBlogsResource.error;
  protected suggestedBlogs = this.suggestedBlogsResource.value;

  protected filtered = signal(false);

  public updateSearch(event: any) {
    this.searchQuery.set(event.target.value)
  }

  protected toggleList(): void {
    this.filtered.update(v => !v);
  }

  protected editBlog(id: string): void {
    const editableBlog = this.blogs()?.find(b => b.id === id);
    this.selectedBlog.set(editableBlog);
    console.log(editableBlog)
  }

  protected closePopover(): void {
    this.selectedBlog.set(null);
  }

  protected updateSelectedBlog(event: any, property: string): void {
    this.selectedBlog.update(b => ({ ...b, [property]: event.target.value }))
  }

  protected updateBlog(): void {
    if (this.selectedBlog().id === '') {
      this.http.post<any>(`http://127.0.0.1:5000/posts`, this.selectedBlog()).subscribe({
        next: () => {
          this.blogsResource.reload();
          this.selectedBlog.set(null);
        }
      })
    } else {
      this.http.put<any>(`http://127.0.0.1:5000/posts/${this.selectedBlog().id}`, this.selectedBlog()).subscribe({
        next: () => {
          this.blogsResource.reload();
          this.selectedBlog.set(null);
        }
      })
    }
  }

  protected deleteBlog(): void {
    this.http.delete<any>(`http://127.0.0.1:5000/posts/${this.selectedBlog().id}`).subscribe({
      next: () => {
        this.blogsResource.reload();
        this.selectedBlog.set(null);
      }
    })
  }

  protected addNewBlog(): void {
    this.selectedBlog.set({ title: '', description: '', content: '', id: '' })
  }
}
