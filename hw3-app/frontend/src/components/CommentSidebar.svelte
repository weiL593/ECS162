<script lang="ts">
  import { onMount } from "svelte";
  import "../styles/CommentSidebar.css";
  export let articleId: string;
  export let articleTitle: string;
  export let onClose: () => void; 

  let comments: any[] = [];
  let newComment = "";

  async function fetchComments() {
    const safeArticleId = encodeURIComponent(articleId);
    const res = await fetch(`/comments/${safeArticleId}`);
    comments = await res.json();
  }

  async function postComment() {
    if (!newComment.trim()) return;
    //Sends a POST Requrest
    const safeArticleId = encodeURIComponent(articleId);

    await fetch(`/comments/${safeArticleId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comment: newComment }),
    });
    newComment = "";
    //reloads comment
    fetchComments();
  }

  onMount(fetchComments);
</script>

<div
  class="sidebar-overlay"
  role="button"
  tabindex="0"
  on:click={onClose}
  on:keydown={(e) => (e.key === "Enter" || e.key === " ") && onClose()}
></div>

<aside class="comment-sidebar">
  <div class="sidebar-header">
    <div class="article-title">
      <strong> {articleTitle} </strong>
    </div>
    <div>
      <button class="close-btn" on:click={onClose}>×</button>
    </div>
  </div>

  <section class="comment-list">
    <h2>Comments {comments.length}</h2>
      {#each comments as comment}
        <div class="comment-item">
          <div class="comment-header">
            <div class="avatar">
              {(comment.user_name || "G").charAt(0).toLowerCase()}
            </div>
            <div class="user-info">
              <strong>{comment.user_name || "Guest"}</strong>
              <small>{new Date(comment.timestamp).toLocaleString()}</small>
            </div>
          </div>
          <p class="comment-text">{comment.comment}</p>
        </div>
      {/each}
  </section>

  <div class="comment-form">
    <textarea
      bind:value={newComment}
      placeholder="Write a comment..."
      rows="2"
    ></textarea>
    <button class="post-btn" on:click={postComment}>Post</button>
  </div>
</aside>
