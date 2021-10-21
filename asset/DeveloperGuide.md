# [1. Python 개발 가이드 문서](http://pms.redpenai.com/confluence/display/DEV4/Python)
### Python Code Style 규칙
- [Python Enhancement Proposal 8 (PEP8)](https://www.python.org/dev/peps/pep-0008/#introduction) 코딩 스타일을 기본으로 한다.
- `@classmethod`와 `@staticmethod`는 사용하지 않는다.
- `PEP8`를 준수하고 가독성 좋은 코드로 자동 수정하기 위하여 [BLACK 포메터](https://github.com/psf/black) 를 사용한다.
- `BLACK 포메터`를 적용 후, 하기와 같이 `--line-length`를 88(Default)에서 119로 변경하여 사용한다. 
```bash 
# Command line options
$ black --line-length 119 
```
* [VSCode : Using Black to automatically format Python](https://dev.to/adamlombard/how-to-use-the-black-python-code-formatter-in-vscode-3lo0)  
### Python Code 명명 규칙
- 함수, 변수, Attribute는 소문자로만 작성하며, **snake case**를 따른다. 예) variable_name
  - `모든 함수명`은 항상 `동사로 시작`하며, 어떠한 동작을 하는지 추측할 수 있게 한다.
  - `모든 변수`는 `명사로 시작`하며, 어떠한 대상을 의미하는지 추측할 수 있게 한다.
  - 단, `Boolean값을 가지는 변수`는 `is_형용사`로 시작하며, 뒤에 나오는 명사가 참인지 거짓인지를 추측할 수 있게 한다.
  - 단, 함수에 전달하는 파라미터는 **camel case**를 따른다. 예) def set_name(userName)
  - 단, RequestModel class와 ResponseModel class에서 사용하는 attribute는 **camel case**를 따른다. 예) self.attributeName
- 클래스는 단어 첫 문자마다 대문자를 사용하여 연결하는 **CapWords** 또는 **Upper Camel Case**를 따른다. 예) ClassName
  - 클래스의 `public attribute`는 밑줄로 시작하지 않는다. 예) name
  - 클래스의 `protected instance attribute`는 하나의 밑줄로 시작한다. 예) _name
  - 클래스의 `private instance attribute`는 두개의 밑줄로 시작한다. 예) __name
- 모듈은 짧은 소문자를 사용하며 **snake case**를 따른다. 
- 패키지명은 짧은 소문자를 사용하며 **snake case**를 따른다.

# 2. Git 가이드 문서
### Git config 작성
```bash
$ git config --global user.name 사용자명
$ git config --global user.email 사용자이메일주소
```
### [Git Branch 가이드](http://pms.redpenai.com/confluence/pages/viewpage.action?pageId=336673)
- **master (or main)**
  - 실제 운영에 적용되는 branch
  - release branch 또는 hotfix branch만 pull request merge의 target이 된다.
  - `개발리더 외에는 Master를 수정하지 않는다.`
- **hotfix**
  - 운영 중 다음 release가 이루어지기 전에 발견된 bug를 급하게 수정 반영해야 할 때 생성한다.
  - `master branch에서 파생된다.` 
  - bugfix가 이루어진 후에는 반드시 develop, release, master branch 모두에 변경내용을 merge하여야 한다.
  - `개발리더 외에는 Master를 수정하지 않는다.`
- **release**
  - QA에 적용되는 branch
  - `develop branch에서 파생된다.`
  - bugfix가 이루어진 후에는 반드시 develop branch에 변경내용을 merge하여야 한다.
  - `개발리더 외에는 Master를 수정하지 않는다.`
- **develop**
  - 개발에 적용되는 branch
  - 최초에 mater branch에서 파생된다.
  - dugfix(release, hotfix) 또는 개발 완료(feature)가 이루어진 경우에는 반드시 develop branch에 변경내용을 merge하여야 한다.
- **feature**
  - 기능 단위의 개발에 적용되는 branch
  - `Jira명(Ticket번호)으로 feature branch 생성해야 한다. 예) feature/AIECO-001`
  - `develop branch에서 파생된다.`
  - 기능 개발이 완료된 경우에는 develop branch에 morge하여야 한다.
### [Git Commit 메시지 가이드](http://pms.redpenai.com/confluence/pages/viewpage.action?pageId=336676)
모든 Commit 메시지는 다음과 같이 세 영역으로 구성되며, 각 영역은 빈 줄로 분리 합니다.
- 제목 : 50자 이내로 작성
  - 유형 : 추가, 수정, 삭제
- 본문(생략 가능) : 한 줄당 72자 내로 작성
- 꼬리말(생략가능) : 관련 jira이슈
```yaml
<유형> 제목

본문(생략 가능)

JIRA : AIECO-001, AIECO-002
```