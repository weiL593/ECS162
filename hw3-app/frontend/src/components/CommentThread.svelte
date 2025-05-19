<script lang="ts">
  import CommentThread from "./CommentThread.svelte";

  export let comment: any;
  export let comments: any[];
  export let replyTo: string | null;
  export let newReply: string;
  export let onReply: (parentId: string, text: string) => void;
  export let setReplyTo: (id: string | null) => void;
  export let currentUser: any;
  export let onDelete: (id: string) => void;
</script>

<div class="comment-item">
  <strong>{comment.user_name}</strong>
  <p>{comment.comment}</p>
  <small>{new Date(comment.timestamp).toLocaleString()}</small>

  <button on:click={() => setReplyTo(comment._id)}>Reply</button>

  {#if currentUser?.email === "moderator@hw3.com"}
    <button class="delete-btn" on:click={() => onDelete(comment._id)}>
      🗑 Delete
    </button>
  {/if}

  {#if replyTo === comment._id}
    <div class="reply-form">
      <textarea bind:value={newReply} placeholder="Write a reply...">></textarea
      >
      <button
        on:click={() => {
          onReply(comment._id, newReply);
          newReply = "";
        }}>Post Reply</button
      >
    </div>
  {/if}

  <!-- Recursively render children -->
  <div class="replies">
    {#each comments.filter((c) => c.parent_id === comment._id) as child}
      <CommentThread
        comment={child}
        {comments}
        {replyTo}
        {newReply}
        {onReply}
        {setReplyTo}
        {currentUser}
        {onDelete}
      />
    {/each}
  </div>
</div>

<style>
  .replies {
    margin-left: 1em;
    border-left: 1px solid #ccc;
    padding-left: 1em;
  }
</style>
