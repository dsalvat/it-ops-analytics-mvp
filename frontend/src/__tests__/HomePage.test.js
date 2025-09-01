import React from 'react';
import { render, screen } from '@testing-library/react';
import HomePage from '../pages/index';

global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve([]),
  })
);

describe('HomePage', () => {
  it('renders a heading', () => {
    render(<HomePage />);

    const heading = screen.getByRole('heading', {
      name: /it operations analytics dashboard/i,
    });

    expect(heading).toBeInTheDocument();
  });
});
