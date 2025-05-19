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
  
    async function fetchComments() {
      const safeArticleId = encodeURIComponent(articleId);
      const res = await fetch(`/comments/${safeArticleId}`);
      comments = await res.json();
    }
  
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
/>

<aside class="comment-sidebar">
  <div class="sidebar-header">
    <div class="article-title">
      <strong>{articleTitle}</strong>
    </div>
    <button class="close-btn" on:click={onClose}>×</button>
  </div>

  <div class="comment-list">
    {#each comments.filter((c) => !c.parent_id) as comment}
      <CommentThread
        {comment}
        {comments}
        {replyTo}
        {newReply}
        onReply={async (parentId, text) => {
          if (!text.trim()) return;
          await postComment(parentId, text);
          newReply = "";
          replyTo = null;
        }}
        setReplyTo={(id) => (replyTo = id)}
      />
    {/each}
  </div>

  <div class="comment-form">
    <textarea
      bind:value={newComment}
      placeholder="Write a comment..."
      rows="2"
    />
    <button
      class="post-btn"
      on:click={() => {
        postComment(null, newComment);
        newComment = "";
      }}
    >Post</button>
  </div>
</aside>
