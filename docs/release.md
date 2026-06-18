# 릴리즈 및 배포 가이드

본 문서는 `yt-dlp-webui` 프로젝트의 릴리즈 배포 절차, Git 태깅, GitHub Actions 파이프라인, 그리고 실패 시 대응 방법을 상세히 설명합니다.

---

## 목차

1. [릴리즈 흐름 개요](#릴리즈-흐름-개요)
2. [정상 릴리즈 절차](#정상-릴리즈-절차)
3. [Git 태깅 상세 가이드](#git-태깅-상세-가이드)
4. [빌드 파이프라인 구조](#빌드-파이프라인-구조)
5. [실패 시 대응 시나리오](#실패-시-대응-시나리오)
6. [버전 규약](#버전-규약)

---

## 릴리즈 흐름 개요

```
로컬 검증 → 커밋 → push → 태그 생성 → 태그 push
                                            │
                                            ▼
                                  GitHub Actions 자동 트리거
                                            │
                          ┌─────────────────┼─────────────────┐
                          ▼                 ▼                 ▼
                     ruff lint         pytest          npm build
                          │                 │                 │
                          └─────────────────┴─────────────────┘
                                            │
                                            ▼
                                  PyInstaller 빌드
                                            │
                                            ▼
                              GitHub Release에 zip 업로드
```

태그 이름이 `v`로 시작하는 경우(`v*`)에만 Actions가 트리거됩니다 (`release.yml` 참고).

---

## 정상 릴리즈 절차

### 1단계: 로컬 사전 검증

태그를 push하기 전에 반드시 로컬에서 모든 검사를 통과시킵니다.
Actions가 실패하면 태그를 다시 만들어야 하므로 사전 검증이 중요합니다.

```powershell
# 백엔드 린트
.\.venv\Scripts\python -m ruff check backend tests

# 백엔드 테스트 전체
.\.venv\Scripts\python -m pytest

# 프론트엔드 빌드 가능 여부 확인
cd frontend
npm run build
cd ..
```

### 2단계: `pyproject.toml` 버전 갱신

```toml
# pyproject.toml
[project]
name = "yt-dlp-webui"
version = "0.1.1"   # ← 배포할 버전으로 수정
```

### 3단계: 커밋 및 main push

```powershell
git add pyproject.toml
git commit -m "chore: bump version to v0.1.1"
git push origin main
```

### 4단계: 릴리즈 태그 생성

annotated tag(`-a`)를 사용합니다. lightweight 태그는 릴리즈 노트가 없어 GitHub Release 자동 생성 시 설명이 비어있습니다.

```powershell
git tag -a v0.1.1 -m "Release v0.1.1

변경 사항을 여기에 간략히 기술합니다."
```

### 5단계: 태그 push → Actions 트리거

```powershell
git push origin v0.1.1
```

push 즉시 GitHub Actions가 트리거됩니다.
진행 상황은 `https://github.com/zhdlxh48/yt-dlp-webui/actions` 에서 확인합니다.

---

## Git 태깅 상세 가이드

### 태그 종류

| 종류 | 명령어 | 설명 |
|---|---|---|
| Annotated tag | `git tag -a v1.0.0 -m "메시지"` | **권장.** 작성자·날짜·메시지 포함. GitHub Release와 연동됨. |
| Lightweight tag | `git tag v1.0.0` | 단순 커밋 포인터. 릴리즈용으로 부적합. |

### 현재 태그 목록 확인

```powershell
# 로컬 태그 목록
git tag -l

# 태그와 해당 커밋 해시 함께 확인
git tag -l --format="%(refname:short) -> %(objectname:short)"

# 특정 태그가 가리키는 커밋 확인
git rev-list -n 1 v0.1.1
```

### 특정 커밋에 태그 달기

기본적으로 `git tag`는 현재 `HEAD`에 태그를 답니다.
과거 커밋에 태그를 달려면 커밋 해시를 마지막에 지정합니다.

```powershell
# HEAD가 아닌 특정 커밋에 태그
git tag -a v0.1.1 -m "Release v0.1.1" <commit-hash>

# 예시: 커밋 해시 확인 후 태그
git log --oneline -10
git tag -a v0.1.1 -m "Release v0.1.1" 16e4ef7
git push origin v0.1.1
```

### 원격 태그 확인

```powershell
# 원격에 push된 태그 목록
git ls-remote --tags origin
```

---

## 빌드 파이프라인 구조

[`.github/workflows/release.yml`](file:///.github/workflows/release.yml)

```
태그 push (v*)
    │
    ▼
Windows 러너 기동 (windows-latest)
    │
    ├─ Checkout
    ├─ Python 3.14 설치
    ├─ Node 24 설치
    ├─ uv 설치
    ├─ Python 의존성 설치  (uv sync --extra dev --extra build)
    ├─ 프론트엔드 의존성    (npm ci)
    ├─ 프론트엔드 빌드      (npm run build)
    ├─ 백엔드 린트          (uv run ruff check backend tests)
    ├─ 백엔드 테스트        (uv run pytest)
    ├─ PyInstaller 빌드     → dist/LiveRecorder/
    ├─ zip 패키징           → yt-dlp-webui-windows-x64-v0.1.1.zip
    └─ GitHub Release 업로드
```

> [!NOTE]
> `v`로 시작하는 태그가 push될 때만 GitHub Release에 zip이 업로드됩니다.
> `v`로 시작하지 않는 태그는 빌드·테스트까지는 수행하지만 Release 업로드는 건너뜁니다.

---

## 실패 시 대응 시나리오

### 시나리오 A: 테스트/린트 실패 — 태그 push 후 Actions 실패

Actions가 `ruff` 또는 `pytest` 단계에서 실패한 경우입니다.

**원인 파악 → 코드 수정 → 커밋 → 태그 재생성 순으로 처리합니다.**

```powershell
# 1. 로컬에서 실패 원인 재현 및 수정
.\.venv\Scripts\python -m ruff check backend tests
.\.venv\Scripts\python -m pytest

# 2. 수정 커밋 push
git add <수정한 파일>
git commit -m "fix: <실패 원인 수정>"
git push origin main

# 3. 기존 태그 삭제 (로컬)
git tag -d v0.1.1

# 4. 기존 태그 삭제 (원격)
git push origin :refs/tags/v0.1.1

# 5. 최신 커밋(HEAD)에 태그 재생성
git tag -a v0.1.1 -m "Release v0.1.1"

# 6. 태그 push → Actions 재트리거
git push origin v0.1.1
```

> [!IMPORTANT]
> `git push origin :refs/tags/<tagname>` 형태가 원격 태그 삭제 명령입니다.
> `refs/tags/` 접두사를 반드시 포함해야 합니다.

---

### 시나리오 B: 빌드 성공 후 zip/Release 업로드 실패

Actions의 패키징 또는 업로드 단계만 실패한 경우, 코드 수정 없이 태그만 재생성합니다.

```powershell
# 로컬·원격 태그 삭제
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1

# HEAD는 그대로, 태그만 재생성
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
```

---

### 시나리오 C: 잘못된 커밋에 태그를 달았을 때

태그가 의도하지 않은 커밋을 가리키고 있을 때 특정 커밋으로 정정합니다.

```powershell
# 현재 태그가 가리키는 커밋 확인
git rev-list -n 1 v0.1.1

# 원하는 커밋 해시 확인
git log --oneline -10

# 태그 삭제 후 올바른 커밋에 재생성
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1
git tag -a v0.1.1 -m "Release v0.1.1" <올바른-커밋-해시>
git push origin v0.1.1
```

---

### 시나리오 D: 실수로 main에 push 후 롤백이 필요한 경우

릴리즈 전 커밋을 되돌려야 하는 경우, 태그 재생성보다 `git revert`를 권장합니다.
`git push --force`는 협업 환경에서 다른 사람의 작업을 파괴할 수 있습니다.

```powershell
# 마지막 커밋 되돌리기 (새 revert 커밋 생성, 히스토리 보존)
git revert HEAD
git push origin main

# 태그가 이미 push된 경우 재생성
git tag -d v0.1.1
git push origin :refs/tags/v0.1.1
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
```

---

### 시나리오 E: 태그가 남아있는데 GitHub Release 페이지가 없는 경우

태그 push는 됐으나 `v*` 패턴 불일치 등으로 Release가 생성되지 않은 경우.

```powershell
# 태그 이름 확인 (소문자 v 여부, 오타 여부)
git tag -l

# 잘못된 태그면 삭제 후 올바른 이름으로 재생성
git tag -d V0.1.1               # 대문자 V 등 잘못된 태그
git push origin :refs/tags/V0.1.1
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin v0.1.1
```

> [!CAUTION]
> 이미 사용자가 다운로드한 버전의 태그를 삭제하면 GitHub Release 링크가 깨집니다.
> 배포 후에는 태그를 삭제하지 말고, 핫픽스 버전(`v0.1.2` 등)을 새로 릴리즈하는 방식을 권장합니다.

---

## 버전 규약

[Semantic Versioning 2.0.0](https://semver.org/lang/ko/) 을 따릅니다.

```
v<MAJOR>.<MINOR>.<PATCH>
```

| 구성요소 | 증가 기준 | 예시 |
|---|---|---|
| `MAJOR` | 하위 호환성이 깨지는 변경 | API 재설계, 설정 파일 포맷 변경 |
| `MINOR` | 하위 호환을 유지하는 새 기능 추가 | 새 설정 옵션, 새 UI 기능 |
| `PATCH` | 버그 수정, 성능 개선 | 크래시 수정, 오타 수정 |

### 태그 이름 형식

```
v{MAJOR}.{MINOR}.{PATCH}
```

- 소문자 `v` 접두사 필수 (Actions 트리거 패턴 `v*` 매칭)
- 예: `v0.1.0`, `v0.1.1`, `v1.0.0`

---

> [!NOTE]
> **보안 권장 사항:**
> 자동 배포 워크플로우는 GitHub의 기본 임시 토큰(`GITHUB_TOKEN`)과 `contents: write` 권한으로 동작합니다.
> 개인 액세스 토큰(PAT)이나 민감한 자격 증명을 저장소 내에 보관하지 않습니다.
