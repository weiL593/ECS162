import { expect, test, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import CommentThread from './CommentThread.svelte';

describe('CommentThread.svelte', () => {
    const baseComment = {
        _id: '123',
        user_name: 'Alice',
        comment: 'This is a test comment.',
        timestamp: new Date().toISOString(),
    };

    const childComment = {
        _id: '456',
        parent_id: '123',
        user_name: 'Bob',
        comment: 'This is a reply.',
        timestamp: new Date().toISOString(),
    };

    const comments = [baseComment, childComment];

    test('renders comment content and reply button', () => {
        const { getByText, getAllByText } = render(CommentThread, {
            props: {
                comment: baseComment,
                comments,
                replyTo: null,
                newReply: '',
                currentUser: { email: 'user@hw3.com' },
                onReply: vi.fn(),
                setReplyTo: vi.fn(),
                onDelete: vi.fn(),
            }
        });

        expect(getByText('Alice')).toBeTruthy();
        expect(getByText('This is a test comment.')).toBeTruthy();
        const replyButtons = getAllByText('Reply');
        expect(replyButtons[0]).toBeTruthy();
    });

    test('shows delete button for moderator', () => {
        const { getByText } = render(CommentThread, {
            props: {
                comment: baseComment,
                comments: [],
                replyTo: null,
                newReply: '',
                currentUser: { email: 'moderator@hw3.com' },
                onReply: vi.fn(),
                setReplyTo: vi.fn(),
                onDelete: vi.fn(),
            }
        });

        expect(getByText('Delete')).toBeTruthy();
    });

    test('calls setReplyTo on reply click and renders reply box when replyTo matches', async () => {
        const mockSetReplyTo = vi.fn();

        const { getByText, getByPlaceholderText, getAllByText } = render(CommentThread, {
            props: {
                comment: baseComment,
                comments,
                replyTo: baseComment._id,
                newReply: 'This is a reply.',
                currentUser: { email: 'moderator@hw3.com' },
                onReply: vi.fn(),
                setReplyTo: mockSetReplyTo,
                onDelete: vi.fn(),
            }
        });

        const replyButtons = getAllByText('Reply');
        await fireEvent.click(replyButtons[0]);
        expect(mockSetReplyTo).toHaveBeenCalledWith('123');

        expect(getByPlaceholderText('Write a reply...')).toBeTruthy();
        expect(getByText('Cancel')).toBeTruthy();
        expect(getByText('Post')).toBeTruthy();
    });

    test('calls onDelete when delete is clicked', async () => {
        const mockDelete = vi.fn();

        const { getAllByText } = render(CommentThread, {
            props: {
                comment: {
                    _id: '123',
                    user_name: 'Alice',
                    comment: 'This is a test comment.',
                    timestamp: new Date().toISOString(),
                },
                comments: [
                    {
                        _id: '123',
                        user_name: 'Alice',
                        comment: 'This is a test comment.',
                        timestamp: new Date().toISOString(),
                    },
                    {
                        _id: '456',
                        parent_id: '123',
                        user_name: 'Bob',
                        comment: 'This is a reply.',
                        timestamp: new Date().toISOString(),
                    },
                ],
                replyTo: null,
                newReply: '',
                currentUser: { email: 'moderator@hw3.com' },
                onReply: vi.fn(),
                setReplyTo: vi.fn(),
                onDelete: mockDelete,
            },
        });

        const deleteButtons = getAllByText('Delete');
        expect(deleteButtons).toHaveLength(2); // one for each comment

        await fireEvent.click(deleteButtons[0]); // Click the parent's delete
        expect(mockDelete).toHaveBeenCalledWith('123');
    });
});
