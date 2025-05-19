<script lang="ts">
    import CommentThread from "./CommentThread.svelte";
    import "../styles/CommentItem.css";

    // props received from parent component
    export let comment: any;
    export let comments: any[];
    export let replyTo: string | null;
    export let newReply: string;
    export let currentUser: any;
    // callback functions passed from parent
    export let onReply: (parentId: string, text: string) => void;
    export let setReplyTo: (id: string | null) => void;
    export let onDelete: (id: string) => void;
  </script>
  
  <!-- container for the entire comment block -->
  <div class="comment-item">
    <div class="comment-header">
      <!-- create the user info and time stamp -->
      <div class="avatar">
        {comment.user_name?.charAt(0).toUpperCase() || "?"}
      </div>
      <div class="user-info">
        <strong class="username">{comment.user_name}</strong>
        <small class="timestamp">
          {new Date(comment.timestamp).toLocaleString()}
        </small>
      </div>
    </div>

    <!-- the comment text box and buttons -->
    <div class="comment-body">
      <p class="comment-text">{comment.comment}</p>
      <!-- show Reply button for everyone  -->
      <div class="comment-actions">
        <button class="reply-link" on:click={() => setReplyTo(comment._id)}>
          Reply
        </button>
        <!-- only show Delete button to moderator -->
        {#if currentUser?.email === "moderator@hw3.com"}
          <button class="delete-btn" on:click={() => onDelete(comment._id)}>
            Delete
          </button>
        {/if}
      </div>
      <!-- create the reply box -->
      {#if replyTo === comment._id}
        <div class="reply-form">
          <textarea
            bind:value={newReply}
            placeholder="Write a reply..."
            rows="2"
          ></textarea>
          <!-- add the buttons in reply box -->
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
  
    <!-- render nested replies -->
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
  