<script lang="ts">
    import CommentThread from "./CommentThread.svelte";
    import "../styles/CommentItem.css";
  
    export let comment: any;
    export let comments: any[];
    export let replyTo: string | null;
    export let newReply: string;
    export let currentUser: any;
    export let onReply: (parentId: string, text: string) => void;
    export let setReplyTo: (id: string | null) => void;
    export let onDelete: (id: string) => void;
  </script>
  
  <div class="comment-item">
    <div class="user-info">
      <strong class="username">{comment.user_name}</strong>
      <small class="timestamp">
        {new Date(comment.timestamp).toLocaleString()}
      </small>
    </div>
  
    <div class="comment-body">
      <p class="comment-text">{comment.comment}</p>
  
      <button class="reply-link" on:click={() => setReplyTo(comment._id)}>
        Reply
      </button>
  
      {#if currentUser?.email === "moderator@hw3.com"}
        <button class="delete-btn" on:click={() => onDelete(comment._id)}>
          🗑 Delete
        </button>
      {/if}
  
      {#if replyTo === comment._id}
        <div class="reply-form">
          <textarea
            bind:value={newReply}
            placeholder="Write a reply..."
            rows="2"
          ></textarea>
          <div class="form-buttons">
            <button class="cancel-btn" on:click={() => setReplyTo(null)}>
              Cancel
            </button>
            <button
              class="post-btn"
              on:click={() => {
                onReply(comment._id, newReply);
                newReply = "";
              }}
              disabled={!newReply.trim()}
            >
              Post
            </button>
          </div>
        </div>
      {/if}
    </div>
  
    <!-- Render nested replies -->
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
  