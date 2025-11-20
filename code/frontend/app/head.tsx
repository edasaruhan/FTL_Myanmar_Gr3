import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Lecture Companion',
  description: 'Generate transcripts from YouTube or files',
};

export default function Head() {
  return (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Lecture Companion</title>
    </>
  );
}
