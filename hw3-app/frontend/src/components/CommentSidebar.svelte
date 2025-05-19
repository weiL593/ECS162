<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import "../styles/CommentSidebar.css";
  import CommentThread from "./CommentThread.svelte";

  export let articleId: string;
  export let articleTitle: string;

  let comments: any[] = [];
  let newComment = "";
  let replyTo: string | null = null;
  let newReply = "";
  const dispatch = createEventDispatcher();

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
  on:click={() => dispatch("close")}
  on:keydown={(e) => (e.key === "Enter" || e.key === " ") && dispatch("close")}
></div>
<aside class="comment-sidebar">
  <div class="sidebar-content">
    <button class="close-btn" on:click={() => dispatch("close")}>×</button>
    <h3>Comments for:</h3>
    <p><em>{articleTitle}</em></p>

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
      <textarea bind:value={newComment} placeholder="Write a comment..."
      ></textarea>
      <button
        on:click={() => {
          postComment(null, newComment);
          newComment = "";
        }}>Post</button
      >
    </div>
  </div>
</aside>
