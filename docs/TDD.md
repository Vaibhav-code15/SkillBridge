# TDD evidence

| Sprint | Phase | Test purpose | Commit | GitHub Actions | Observed result | Explanation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RED | Case-insensitive duplicate names | `2760066e39ee29a11ecb4fbee6e8ea4c9c739928` | [Run 45471150169](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45471150169) | Failed | The exact-case comparison did not recognize `python` as `Python`. |
| 1 | GREEN | Case-insensitive duplicate names | `6fa29ea56ad85379c619ee6cb52e8269458d0c48` | [Run 45471349883](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45471349883) | Passed | Comparison normalizes case. |
| 1 | REFACTOR | Case-insensitive duplicate names | `79a42e899307f49098f18a07ecacd5541f143d41` | [Run 45471571181](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45471571181) | Passed | Candidate normalization is performed once. |
| 2 | Pending | Pending | Pending | Pending | Pending | Pending |
| 3 | Pending | Pending | Pending | Pending | Pending | Pending |

The catalogue form now uses the service, and a database constraint separately enforces uniqueness using `Lower(name)`. The refactor is small; its educational value should be assessed during review.
