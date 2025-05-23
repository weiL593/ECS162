<script lang="ts">
  import { onMount } from "svelte";
  import "../styles/CommentSidebar.css";
  import CommentThread from "./CommentThread.svelte";

  export let articleId: string;
  export let articleTitle: string;
  export let onClose: () => void;

  let comments: any[] = [];
  let newComment = "";
  let replyTo: string | null = null;
  let newReply = "";
  let currentUser: any = null;

  // fetch the comments for this article
  async function fetchComments() {
    const safeArticleId = encodeURIComponent(articleId);
    const res = await fetch(`/comments/${safeArticleId}`);
    comments = await res.json();
  }
  // post a new comment
  async function postComment(parentId: string | null, text: string) {
    const safeArticleId = encodeURIComponent(articleId);
    await fetch(`/comments/${safeArticleId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        comment: text,
        parent_id: parentId,
      }),
    });
    await fetchComments();
  }
  // fetch the logged-in user
  async function fetchUser() {
    const res = await fetch("/me");
    if (res.ok) currentUser = await res.json();
  }

  onMount(() => {
    fetchUser();
    fetchComments();
  });
</script>

<!-- semi-transparent account sidebar -->
<div
  class="sidebar-overlay"
  role="button"
  tabindex="0"
  on:click={onClose}
  on:keydown={(e) => (e.key === "Enter" || e.key === " ") && onClose()}
></div>

<!-- the main section of comment sidebar -->
<aside class="comment-sidebar">
  <!-- the header of comment sidebar -->
  <div class="sidebar-header">
    <div class="article-title">
      <strong>{articleTitle}</strong>
    </div>
    <button class="close-btn" on:click={onClose}>×</button>
  </div>

    <!-- comments section -->
  <div class="comment-list">
    <h2>Comments {comments.length}</h2>
    <!-- show each items in order -->
    <!-- handle the reple and delect events -->
    {#each comments.filter((c) => !c.parent_id) as comment}
      <CommentThread
        {comment}
        {comments}
        {replyTo}
        {newReply}
        {currentUser}
        onReply={async (parentId, text) => {
          if (!text.trim()) return;
          await postComment(parentId, text);
          newReply = "";
          replyTo = null;
        }}
        onDelete={async (id) => {
          await fetch(`/comments/${id}`, { method: "DELETE" });
          await fetchComments();
        }}
        setReplyTo={(id) => (replyTo = id)}
      />
    {/each}
  </div>
<!-- write the comment -->
<div class="comment-form">
  <textarea
    class="comment-textarea"
    bind:value={newComment}
    placeholder="Write a comment..."
    rows="3"
  ></textarea>
  <!-- create the cnacle and post buttons -->
  <div class="form-buttons">
    <button class="cancel-btn" on:click={() => (newComment = "")}>Cancel</button>
    <button
      class="post-btn"
      disabled={!newComment.trim()}
      on:click={() => {
        if (!newComment.trim()) return;
        postComment(null, newComment);
        newComment = "";
      }}
    >
      Post
    </button>
  </div>
</div>

</aside>
