# TDD evidence

| Sprint | Phase | Test purpose | Commit | GitHub Actions | Observed result | Explanation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RED | Case-insensitive duplicate names | `2760066e39ee29a11ecb4fbee6e8ea4c9c739928` | [Run 45471150169](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45471150169) | Failed | The exact-case comparison did not recognize `python` as `Python`. |
| 1 | GREEN | Case-insensitive duplicate names | `6fa29ea56ad85379c619ee6cb52e8269458d0c48` | [Run 45471349883](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45471349883) | Passed | Comparison normalizes case. |
| 1 | REFACTOR | Case-insensitive duplicate names | `79a42e899307f49098f18a07ecacd5541f143d41` | [Run 45471571181](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45471571181) | Passed | Candidate normalization is performed once. |
| 2 | RED | Weighted full, zero, partial and weighted fit; classifications; unscored empty input; validation; half-up rounding | `59e25fb2c13176d802f03644aa815207c93c98fc` | [Run 45661210561](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45661210561) | Failed | Seven engine tests reached the intentional `NotImplementedError`; all 11 Sprint 1 tests passed. |
| 2 | GREEN | Same US13 weighted matching engine tests | `40972c35a52e38a3134774d995b794e139c1aa14` | [Run 45661626486](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45661626486) | Passed | Exact fractional credits and contributions produce the weighted score with half-up rounding. |
| 2 | REFACTOR | Same US13 weighted matching engine tests | `00d70e60798406ef6205fcfb13eaa140afc73814` | [Run 45661942022](https://github.com/Vaibhav-code15/SkillBridge/actions/runs/45661942022) | Passed | Extracted classification/credit and half-up rounding helpers without changing behavior. |
| 3 | Pending | Pending | Pending | Pending | Pending | Pending |

The catalogue form now uses the service, and a database constraint separately enforces uniqueness using `Lower(name)`. The refactor is small; its educational value should be assessed during review.
