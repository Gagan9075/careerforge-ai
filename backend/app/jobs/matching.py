from app.jobs.skill_normalizer import parse_skills


class JobMatchingService:

    def calculate_match(
        self,
        resume_skills: str | None,
        job_skills: str | None,
    ) -> dict:

        resume_skill_list = set(
            parse_skills(resume_skills)
        )

        job_skill_list = set(
            parse_skills(job_skills)
        )

        # No structured job skills available
        if not job_skill_list:
            return {
                "match_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "skills_available": False,
                "note": (
                    "Match results may differ because this job "
                    "does not provide a structured skills section. "
                    "Please review the full job description for "
                    "additional skills and requirements."
                ),
            }

        matched_skills = sorted(
            resume_skill_list.intersection(job_skill_list)
        )

        missing_skills = sorted(
            job_skill_list.difference(resume_skill_list)
        )

        match_score = round(
            (len(matched_skills) / len(job_skill_list)) * 100
        )

        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skills_available": True,
            "note": (
                "Match results are based on the structured skills "
                "available in the job listing. Some companies may "
                "mention additional skills only in the job "
                "description, so please review the full description."
            ),
        }