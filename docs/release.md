# 릴리즈 및 배포 가이드

본 문서는 `yt-dlp-webui` 프로젝트의 릴리즈 배포 절차와 자동 빌드 환경에 대해 상세히 설명합니다.

---

## 릴리즈 수행 절차 (Release Procedure)

버전 배포는 깃 배포 태그(Git Release Tag)를 생성하여 진행하며, GitHub Actions를 통해 빌드와 릴리즈가 자동으로 수행됩니다.

### 1. 로컬 코드 사전 검증
코드를 커밋하고 배포하기 전에 반드시 아래 명령어를 로컬 터미널에서 구동하여 모든 정적 검사 및 단위 테스트가 통과하는지 사전 확인합니다.
```powershell
# 1) 백엔드 코드 스타일 및 린터 검증
.\.venv\Scripts\python -m ruff check backend tests

# 2) 파이테스트 단위 테스트 전체 실행
.\.venv\Scripts\python -m pytest

# 3) 프론트엔드 정적 파일 프로덕션 빌드 성공 여부 검사
cd frontend
npm run build
cd ..
```

### 2. 버전 정보 갱신
`pyproject.toml` 파일 내의 프로젝트 버전을 배포하려는 버전(예: `version = "0.1.0"`)으로 업데이트합니다.
```toml
# pyproject.toml
[project]
name = "yt-dlp-webui"
version = "0.1.0"
```

### 3. 변경 사항 커밋 및 푸시
수정된 코드와 버전 갱신 사항을 스테이징하고 커밋을 완료합니다.
```powershell
git add .
git commit -m "chore: release version v0.1.0"
git push origin main
```

### 4. 릴리즈 태그 생성 및 배포 푸시
`pyproject.toml`에 기입한 버전과 일치하는 배포용 태그(예: `v0.1.0`)를 생성하여 리포지토리에 푸시합니다.
```powershell
git tag v0.1.0
git push origin v0.1.0
```

---

## 빌드 파이프라인 (Build Pipeline)

배포 태그(`v*`)가 원격 저장소에 푸시되면 GitHub Actions 워크플로우가 자동으로 기동합니다.

1. **자동 빌드 환경:** GitHub Actions 러너가 Windows 빌드 환경을 구축합니다.
2. **패키징:** `PyInstaller`를 활용하여 FastAPI 서버 백엔드 및 정적 빌드된 Svelte 프론트엔드 에셋을 패키징하여 하나의 압축형 윈도우 실행 파일 폴더 구조(`onedir` 형태)를 구축합니다. 결과물 실행 파일 이름은 `LiveRecorder.exe`입니다.
3. **업로드:** 최종 패키지 압축 파일인 `yt-dlp-webui-windows-x64-v0.1.0.zip`을 빌드 완료 후 해당 깃 태그에 해당하는 GitHub Release 릴리즈 페이지에 파일 자산(Asset)으로 자동 업로드합니다.

> [!NOTE]
> **보안 권장 사항:**
> 자동 배포 워크플로우는 GitHub의 기본 임시 토큰(`GITHUB_TOKEN`)과 `contents: write` 쓰기 권한을 사용하여 구동됩니다. 관리자의 개인 액세스 토큰(Personal Access Token, PAT)이나 민감한 자격 증명을 깃 저장소 내에 보관하거나 주입하지 않습니다.
