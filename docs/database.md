# 데이터베이스 및 마이그레이션 가이드

`yt-dlp-webui`는 라이브 채널 설정 및 추후 추가될 동적 데이터를 효율적으로 다루기 위해 SQLite 데이터베이스와 SQLAlchemy ORM을 사용합니다. 본 문서는 데이터베이스 구조 및 마이그레이션 도구(`db_migrate.bat`)의 사용법을 설명합니다.

---

## 데이터베이스 설계 및 아키텍처

### 1. 기술 스택
- **Database Engine:** SQLite (서버리스, 가볍고 파일 기반으로 Windows 환경에 최적화)
- **Object Relational Mapper (ORM):** SQLAlchemy 2.0+ (객체 지향적인 데이터 모델링 및 RAW SQL 제거)

### 2. 초기화 방식
애플리케이션 구동 시 `Base.metadata.create_all(bind=self.engine)` 메서드가 자동으로 호출됩니다.
- 아직 생성되지 않은 테이블이 있다면 클래스 모델 선언을 기반으로 SQLite 데이터베이스 파일(`webui.db`)에 즉시 테이블을 생성합니다.
- 개발 단계나 테스트 환경에서는 번거로운 마이그레이션 파일 생성 및 적용 단계 없이 데이터베이스 모델 추가만으로 즉시 연동됩니다.

### 3. 레거시 데이터 마이그레이션
- 이전 버전에서 사용되던 `settings.toml` 파일 내부의 라이브 채널 정보(`live.channels`)는 최초 앱 실행 시 SQLite 데이터베이스로 자동 이관됩니다.
- 이관이 성공적으로 완료되면 설정 파일에서 해당 채널 항목이 자동으로 삭제되어 단일 진실 공급원(Single Source of Truth) 규칙을 유지합니다.

---

## 마이그레이션 관리 (`db_migrate.bat`)

데이터베이스 모델 스키마가 확정된 상태에서 변경 이력을 파일(버전) 형태로 관리하고 추적해야 할 경우, 마이그레이션 도구인 Alembic과 배치 스크립트를 사용합니다.

### 1. Alembic 초기 환경 구축
프로젝트 루트 디렉토리에서 다음 명령어를 한 번만 실행합니다. 이 명령은 필요한 패키지(`alembic`)를 가상 환경에 설치하고 연동 설정을 완료합니다.
```powershell
.\db_migrate.bat init
```

### 2. 마이그레이션 버전 파일 생성
`backend/ytdlp_webui/core/database.py` 소스코드에서 ORM 모델 클래스를 변경한 후, 기존 DB 상태와의 차이점을 자동으로 분석하여 마이그레이션 파일을 만듭니다.
```powershell
.\db_migrate.bat generate "변경사항_메시지"
# 예: .\db_migrate.bat generate "add_download_history"
```
*(이때 생성되는 파일은 RAW SQL 쿼리가 아닌, Alembic의 파이썬 DDL 메서드 기반 코드로 작성되어 데이터베이스 환경에 안전하게 매핑됩니다.)*

### 3. 마이그레이션 반영
생성된 마이그레이션 변경 사항을 실제 데이터베이스에 최종 적용합니다.
```powershell
.\db_migrate.bat upgrade
```

### 4. 마이그레이션 역사 조회
지금까지 거쳐온 마이그레이션 버전들의 전체 이력을 확인합니다.
```powershell
.\db_migrate.bat history
```
