import { test, vi, expect } from 'vitest';
import { render, waitFor, screen } from '@testing-library/svelte';
import NewYorkTimes from './NewYorkTimes.svelte';

test('renders article headline correctly', async () => {
    const fetchMock = vi.fn()
      // 1. /api/key
      .mockResolvedValueOnce({
        json: () => Promise.resolve({ apiKey: 'test-key' }),
      })
      // 2. NYT articles
      .mockResolvedValueOnce({
        json: () => Promise.resolve({
          response: {
            docs: [
              {
                _id: 'nyt://abc',
                headline: { main: 'Fake News' },
                abstract: 'A test article',
                multimedia: [{ url: 'test.jpg' }],
                web_url: 'https://example.com'
              }
            ]
          }
        }),
      })
      // 3. /comments/nyt://abc
      .mockResolvedValueOnce({
        json: () => Promise.resolve([{ text: 'test comment' }])
      })
      // 4. /me
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ email: 'test@example.com' })
      });
  
    vi.stubGlobal('fetch', fetchMock);
  
    render(NewYorkTimes);
  
    await waitFor(() => {
      expect(screen.getByText('Fake News')).toBeTruthy();
      expect(screen.getByText('💬 1')).toBeTruthy();  // 1 comment
    });
  });
  
  
