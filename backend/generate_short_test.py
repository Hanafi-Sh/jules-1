import asyncio
import json
from app.services.orchestrator import generate_structural_tree_async
from app.services.agents import (
    ContentAuthor, ContentReviewer,
    Formatter,
    QuizMaster, QuizReviewer,
    QuestionSuggester, QuestionReviewer
)
from app.services.json_structurer import JSONStructurer

async def dummy_update_progress(msg: str):
    print(f"[PROGRESS] {msg}")

async def main():
    # Make the topic super simple to guarantee it only generates 1 phase, 1 chapter, 1 level.
    target_skill = "Cara Menyapa (Hello World) dalam Python"
    user_context = "Saya sama sekali tidak bisa programming."

    print("\n=======================================================")
    print("1. MEMBANGUN STRUKTUR KURIKULUM (DAG TREE)")
    print("=======================================================")

    course = await generate_structural_tree_async(target_skill, user_context, dummy_update_progress)

    if not course.phases or not course.phases[0].chapters:
        print("Gagal membuat struktur Bab.")
        return

    first_phase = course.phases[0]
    first_chapter = first_phase.chapters[0]

    print(f"\n=======================================================")
    print(f"2. MEMBANGUN KONTEN UNTUK BAB 1: {first_chapter.title}")
    print("=======================================================")

    course_context_json = course.model_dump_json(exclude={"phases": {"__all__": {"chapters": {"__all__": {"levels"}}}}})

    with open("PYTORCH_BAB_1.md", "w", encoding="utf-8") as f:
        f.write(f"# Course: {course.title}\n")
        f.write(f"## Phase: {first_phase.title}\n")
        f.write(f"### Bab 1: {first_chapter.title}\n")
        f.write(f"> {first_chapter.description}\n\n")
        f.write("---\n\n")

        # Only process the FIRST level to save time
        level = first_chapter.levels[0]
        print(f"\n>> Sedang memproses Level 1: {level.title}...")

        print("   - Agent 4: Content Author...")
        draft_content = await ContentAuthor.write_content(level.title, level.description, target_skill, course_context_json)

        print("   - Agent 4.1: Content Reviewer...")
        refined_content = await ContentReviewer.refine_content(draft_content, level.title, course_context_json)

        print("   - Agent 5: Formatter (UI Markdown)...")
        formatted_content = await Formatter.format_content(refined_content)

        print("   - Agent 7: Curiosity Suggester...")
        draft_q_text = await QuestionSuggester.suggest_questions(formatted_content, course_context_json)

        print("   - Agent 7.1: Curiosity Reviewer...")
        refined_q_text = await QuestionReviewer.refine_questions(draft_q_text, formatted_content, course_context_json)

        print("   - JSON Structurer (Mengambil pertanyaan)...")
        final_questions = await JSONStructurer.extract_suggested_questions(refined_q_text)

        f.write(f"#### Level 1: {level.title}\n")
        f.write(f"{formatted_content}\n\n")
        f.write("**Pertanyaan Curiosity AI:**\n")
        for q in final_questions:
            f.write(f"- 💡 {q}\n")

    print("\nSELESAI. File 'PYTORCH_BAB_1.md' telah disimpan.")

if __name__ == "__main__":
    asyncio.run(main())
