import re

from app.resume.model import Resume


class ATSService:

    def analyze_resume(self, resume: Resume) -> dict:
        completeness_score = self._calculate_completeness(resume)
        skills_score = self._calculate_skills(resume)
        experience_score = self._calculate_experience(resume)
        projects_score = self._calculate_projects(resume)
        education_score = self._calculate_education(resume)
        certifications_score = self._calculate_certifications(resume)
        structure_score = self._calculate_structure(resume)
        contact_score = self._calculate_contact(resume)

        overall_score = (
            completeness_score
            + skills_score
            + experience_score
            + projects_score
            + education_score
            + certifications_score
            + structure_score
            + contact_score
        )

        strengths = []
        improvements = []

        if skills_score >= 15:
            strengths.append("Resume contains a strong technical skills section.")
        else:
            improvements.append("Add more relevant technical skills.")

        if experience_score >= 10:
            strengths.append("Resume contains relevant experience.")
        else:
            improvements.append("Add or improve professional experience details.")

        if projects_score >= 10:
            strengths.append("Resume contains project experience.")
        else:
            improvements.append("Add more relevant projects with measurable outcomes.")

        if education_score >= 7:
            strengths.append("Education information is clearly provided.")
        else:
            improvements.append("Improve the education section.")

        if certifications_score >= 3:
            strengths.append("Certifications are included.")
        else:
            improvements.append("Add relevant certifications if available.")

        if contact_score == 5:
            strengths.append("Contact information is present.")
        else:
            improvements.append("Add complete contact information.")

        return {
            "overall_score": overall_score,
            "completeness_score": completeness_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "projects_score": projects_score,
            "education_score": education_score,
            "certifications_score": certifications_score,
            "structure_score": structure_score,
            "contact_score": contact_score,
            "strengths": strengths,
            "improvements": improvements,
        }

    def _calculate_completeness(self, resume: Resume) -> int:
        fields = [
            resume.summary,
            resume.skills,
            resume.experience,
            resume.education,
            resume.projects,
            resume.certifications,
        ]

        completed_fields = sum(
            1 for field in fields
            if field and field.strip()
        )

        return round((completed_fields / len(fields)) * 20)

    def _calculate_skills(self, resume: Resume) -> int:
        if not resume.skills:
            return 0

        skills = [
            skill.strip()
            for skill in re.split(r"[,|\n]", resume.skills)
            if skill.strip()
        ]

        if len(skills) >= 10:
            return 20

        if len(skills) >= 7:
            return 17

        if len(skills) >= 5:
            return 14

        if len(skills) >= 3:
            return 10

        return 5

    def _calculate_experience(self, resume: Resume) -> int:
        if not resume.experience:
            return 0

        text_length = len(resume.experience.strip())

        if text_length >= 500:
            return 15

        if text_length >= 300:
            return 12

        if text_length >= 150:
            return 9

        return 5

    def _calculate_projects(self, resume: Resume) -> int:
        if not resume.projects:
            return 0

        text_length = len(resume.projects.strip())

        if text_length >= 500:
            return 15

        if text_length >= 300:
            return 12

        if text_length >= 150:
            return 9

        return 5

    def _calculate_education(self, resume: Resume) -> int:
        if not resume.education:
            return 0

        return 10

    def _calculate_certifications(self, resume: Resume) -> int:
        if not resume.certifications:
            return 0

        certifications = [
            item.strip()
            for item in resume.certifications.splitlines()
            if item.strip()
        ]

        if len(certifications) >= 2:
            return 5

        return 3

    def _calculate_structure(self, resume: Resume) -> int:
        sections = [
            resume.summary,
            resume.skills,
            resume.experience,
            resume.education,
            resume.projects,
            resume.certifications,
        ]

        completed_sections = sum(
            1 for section in sections
            if section and section.strip()
        )

        if completed_sections >= 6:
            return 10

        if completed_sections >= 4:
            return 7

        if completed_sections >= 2:
            return 4

        return 0

    def _calculate_contact(self, resume: Resume) -> int:
        score = 0

        if resume.name and resume.name.strip():
            score += 1

        if resume.email and resume.email.strip():
            score += 2

        if resume.phone and resume.phone.strip():
            score += 1

        if resume.location and resume.location.strip():
            score += 1

        return score