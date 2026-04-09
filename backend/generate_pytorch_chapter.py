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
    target_skill = "PyTorch (Deep Learning)"
    user_context = "Saya bisa Python dasar dan konsep Array/Matriks 1D/2D, tapi saya belum pernah menyentuh Machine Learning, Deep Learning, apalagi PyTorch."

    print("\n=======================================================")
    print("1. MEMBANGUN STRUKTUR KURIKULUM (DAG TREE)")
    print("=======================================================")

    # 1. Bangun Struktur
    course = await generate_structural_tree_async(target_skill, user_context, dummy_update_progress)

    # Ambil Chapter (Bab) pertama dari Phase (Pilar) pertama
    if not course.phases or not course.phases[0].chapters:
        print("Gagal membuat struktur Bab.")
        return

    first_phase = course.phases[0]
    first_chapter = first_phase.chapters[0]

    print(f"\n=======================================================")
    print(f"2. MEMBANGUN KONTEN UNTUK BAB 1: {first_chapter.title}")
    print(f"   Pilar (Phase): {first_phase.title}")
    print(f"   Jumlah Level: {len(first_chapter.levels)}")
    print("=======================================================")

    # Prefix context caching (Exclude content that doesn't exist yet)
    course_context_json = course.model_dump_json(exclude={"phases": {"__all__": {"chapters": {"__all__": {"levels"}}}}})

    with open("PYTORCH_BAB_1.md", "w", encoding="utf-8") as f:
        f.write(f"# Course: {course.title}\n")
        f.write(f"## Phase: {first_phase.title}\n")
        f.write(f"### Bab 1: {first_chapter.title}\n")
        f.write(f"> {first_chapter.description}\n\n")
        f.write("---\n\n")

        # Proses semua level di dalam Bab 1 secara berurutan agar rapi di file markdown
        for i, level in enumerate(first_chapter.levels):
            print(f"\n>> Sedang memproses Level {i+1}: {level.title}...")

            # Content Author & Reviewer
            print("   - Agent 4: Content Author...")
            draft_content = await ContentAuthor.write_content(level.title, level.description, target_skill, course_context_json)

            print("   - Agent 4.1: Content Reviewer...")
            refined_content = await ContentReviewer.refine_content(draft_content, level.title, course_context_json)

            # Formatter
            print("   - Agent 5: Formatter (UI Markdown)...")
            formatted_content = await Formatter.format_content(refined_content)

            # Curiosity Questions
            print("   - Agent 7: Curiosity Suggester...")
            draft_q_text = await QuestionSuggester.suggest_questions(formatted_content, course_context_json)

            print("   - Agent 7.1: Curiosity Reviewer...")
            refined_q_text = await QuestionReviewer.refine_questions(draft_q_text, formatted_content, course_context_json)

            print("   - JSON Structurer (Mengambil pertanyaan)...")
            final_questions = await JSONStructurer.extract_suggested_questions(refined_q_text)

            # Tulis ke file
            f.write(f"#### Level {i+1}: {level.title}\n")
            f.write(f"{formatted_content}\n\n")
            f.write("**Pertanyaan Curiosity AI:**\n")
            for q in final_questions:
                f.write(f"- 💡 {q}\n")
            f.write("\n---\n\n")

    print("\nSELURUH PROSES SELESAI. File 'PYTORCH_BAB_1.md' dan 'llm_api_logs.jsonl' telah disimpan.")

if __name__ == "__main__":
    asyncio.run(main())
