import re


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 1200,
        chunk_overlap: int = 150,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _clean_text(
        self,
        text: str,
    ) -> str:

        # Normalize line endings
        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        # Remove repeated spaces/tabs
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        # Remove excessive blank lines
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def split(
        self,
        text: str,
    ) -> list[str]:

        text = self._clean_text(text)

        if not text:
            return []

        # First try to preserve paragraphs
        paragraphs = re.split(
            r"\n\s*\n",
            text,
        )

        paragraphs = [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:

            # If adding the paragraph keeps us
            # within the target size, keep it together.
            if (
                len(current_chunk)
                + len(paragraph)
                + 1
                <= self.chunk_size
            ):

                if current_chunk:
                    current_chunk += "\n\n"

                current_chunk += paragraph

                continue

            # Save current chunk
            if current_chunk:
                chunks.append(
                    current_chunk.strip()
                )

            # If this paragraph itself is too large,
            # split it further.
            if len(paragraph) > self.chunk_size:

                paragraph_chunks = (
                    self._split_large_paragraph(
                        paragraph
                    )
                )

                chunks.extend(
                    paragraph_chunks[:-1]
                )

                current_chunk = (
                    paragraph_chunks[-1]
                )

            else:
                current_chunk = paragraph

        # Add remaining chunk
        if current_chunk:
            chunks.append(
                current_chunk.strip()
            )

        # Add overlap between chunks
        return self._add_overlap(
            chunks
        )

    def _split_large_paragraph(
        self,
        paragraph: str,
    ) -> list[str]:

        words = paragraph.split()

        chunks = []
        current = []

        current_length = 0

        for word in words:

            word_length = (
                len(word) + 1
            )

            if (
                current
                and current_length
                + word_length
                > self.chunk_size
            ):

                chunks.append(
                    " ".join(current)
                )

                current = []
                current_length = 0

            current.append(word)

            current_length += word_length

        if current:
            chunks.append(
                " ".join(current)
            )

        return chunks

    def _add_overlap(
        self,
        chunks: list[str],
    ) -> list[str]:

        if not chunks:
            return []

        result = []

        for index, chunk in enumerate(
            chunks
        ):

            if index == 0:

                result.append(chunk)

                continue

            previous_chunk = chunks[
                index - 1
            ]

            overlap_text = (
                previous_chunk[
                    -self.chunk_overlap:
                ]
            )

            combined = (
                overlap_text
                + "\n\n"
                + chunk
            )

            result.append(
                combined.strip()
            )

        return result