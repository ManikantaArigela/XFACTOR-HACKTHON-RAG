from flask import current_app


def generate_answer(query, records):
    if not records:
        return "I could not find relevant content for that question."

    context = "\n\n".join(
        f"Title: {record.title}\nCategory: {record.category}\nDescription: {record.description}"
        for record in records
    )
    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return f"Relevant content:\n\n{context}"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=current_app.config["RAG_MODEL"],
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "Answer using only the supplied context. Say when the context is insufficient.",
                },
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as error:
        raise RuntimeError("RAG generation failed") from error
