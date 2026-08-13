# Third-Party Notices

Pulsar itself is distributed under the MIT licence — see [`LICENSE`](LICENSE). It
links and ships third-party components that carry their own licences and their own
attribution requirements. Those components are enumerated below, and every notice
their licences require is reproduced here in full.

## Scope — what is covered, and why

Every component listed here is resolved by Swift Package Manager into the app's
build graph and compiled by `swift build -c release`. The authoritative list of
versions is [`macos/Pulsar/Package.resolved`](macos/Pulsar/Package.resolved); the
versions recorded below were read from it.

- **Sparkle** ships as a separate embedded framework at
  `Pulsar.app/Contents/Frameworks/Sparkle.framework` (embedded and ad-hoc signed by
  `scripts/build-pulsar-app.sh`).
- **The Swift packages** are statically linked into the `Pulsar` executable at
  `Pulsar.app/Contents/MacOS/Pulsar`. Two are direct dependencies (Sparkle and
  Hummingbird, declared in `macos/Pulsar/Package.swift`); the rest arrive
  transitively through Hummingbird.
- Where a resolved package also builds targets Pulsar does not link (test kits,
  benchmarks, example servers), the package is still listed. A complete superset
  is the safe notice.

Pulsar ships **two** speech engines, and they carry different obligations:

- **macOS `say` / AVFoundation** (the default) — Apple system frameworks, present on
  the user's machine, neither bundled nor redistributed here, and carrying no
  third-party attribution obligation.
- **Kokoro** (opt-in, off until the user downloads it) — a third-party on-device
  neural synthesiser that IS redistributed in the app. It is statically linked from
  `macos/Pulsar/Vendor/kokoro-swift` (Apache-2.0, vendored in-tree rather than
  fetched by URL) together with MLX Swift (MIT). Its Metal shader library,
  `mlx.metallib` (MIT), is fetched at build time by
  `scripts/fetch-mlx-metallib.sh` and **redistributed inside the app bundle** at
  `Pulsar.app/Contents/MacOS/mlx.metallib`, so it is a distributed binary and is
  noticed accordingly in §6.

Kokoro's G2P is MisakiSwift, vendored inside kokoro-swift and covered by that
repository's Apache-2.0 grant. It is pure Swift: Pulsar does **not** link or ship
espeak-ng, and therefore takes on no GPL obligation from the speech path.

The Kokoro **model weights** (Kokoro-82M, Apache-2.0) are not redistributed. They
are downloaded by the user, on demand, from Hugging Face at first use and stored
outside the app bundle in Application Support.

No analytics SDK is linked, and neither engine sends audio or text off the machine.

**Keep this current:** when `Package.resolved` changes — a version bump, an added
or dropped dependency — re-check this file. `scripts/build-pulsar-app.sh` copies it
into `Pulsar.app/Contents/Resources/THIRD-PARTY-NOTICES.md` so the shipped app
carries its own notices.

## Components

| Component | Version | Licence | Notices |
|---|---|---|---|
| [Sparkle](https://github.com/sparkle-project/Sparkle) | 2.9.1 | MIT (plus five separately-licensed vendored components) | [§1](#1-sparkle--mit) |
| [Hummingbird](https://github.com/hummingbird-project/hummingbird) | 2.22.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [AsyncHTTPClient](https://github.com/swift-server/async-http-client) | 1.33.1 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [Swift Algorithms](https://github.com/apple/swift-algorithms) | 1.2.1 | Apache-2.0 with Runtime Library Exception | [§2.1](#21-apache-license-20--full-text) |
| [SwiftASN1](https://github.com/apple/swift-asn1) | 1.7.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [Swift Async Algorithms](https://github.com/apple/swift-async-algorithms) | 1.1.3 | Apache-2.0 with Runtime Library Exception | [§2.1](#21-apache-license-20--full-text) |
| [Swift Atomics](https://github.com/apple/swift-atomics) | 1.3.0 | Apache-2.0 with Runtime Library Exception | [§2.1](#21-apache-license-20--full-text) |
| [SwiftCertificates](https://github.com/apple/swift-certificates) | 1.19.1 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [Swift Collections](https://github.com/apple/swift-collections) | 1.5.0 | Apache-2.0 with Runtime Library Exception | [§2.1](#21-apache-license-20--full-text) |
| [SwiftConfiguration](https://github.com/apple/swift-configuration) | 1.2.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftCrypto](https://github.com/apple/swift-crypto) | 4.5.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [Swift Distributed Tracing](https://github.com/apple/swift-distributed-tracing) | 1.4.1 | Apache-2.0 | [§2.1](#21-apache-license-20--full-text) |
| [Swift HTTP Structured Headers](https://github.com/apple/swift-http-structured-headers) | 1.7.0 | Apache-2.0 | [§2.1](#21-apache-license-20--full-text) |
| [Swift HTTP Types](https://github.com/apple/swift-http-types) | 1.5.1 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftLog](https://github.com/apple/swift-log) | 1.12.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftMetrics](https://github.com/apple/swift-metrics) | 2.10.1 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftNIO](https://github.com/apple/swift-nio) | 2.99.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftNIO Extras](https://github.com/apple/swift-nio-extras) | 1.34.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftNIO HTTP/2](https://github.com/apple/swift-nio-http2) | 1.43.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftNIO SSL](https://github.com/apple/swift-nio-ssl) | 2.37.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [SwiftNIO Transport Services](https://github.com/apple/swift-nio-transport-services) | 1.28.0 | Apache-2.0 | [§2.1](#21-apache-license-20--full-text) |
| [Swift Numerics](https://github.com/apple/swift-numerics) | 1.1.1 | Apache-2.0 with Runtime Library Exception | [§2.1](#21-apache-license-20--full-text) |
| [Swift Service Context](https://github.com/apple/swift-service-context) | 1.3.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [Swift Service Lifecycle](https://github.com/swift-server/swift-service-lifecycle) | 2.11.0 | Apache-2.0 | [§2.3](#23-required-notice-content) |
| [Swift System](https://github.com/apple/swift-system) | 1.6.4 | Apache-2.0 with Runtime Library Exception | [§2.1](#21-apache-license-20--full-text) |
| [kokoro-swift](https://github.com/mweinbach/kokoro-swift) (vendored, incl. its MisakiSwift G2P) | 20bf04c | Apache-2.0 | [§2.1](#21-apache-license-20--full-text) |
| [MLX Swift](https://github.com/ml-explore/mlx-swift) | 0.31.3 | MIT | [§6](#6-mlx--mit) |
| [MLX Metal shader library](https://pypi.org/project/mlx-metal/) (`mlx.metallib`, redistributed binary) | 0.31.1 | MIT | [§6](#6-mlx--mit) |

Vendored and derived code carried *inside* those components — BoringSSL, llhttp,
zlib and the rest — is listed in [§3](#3-code-vendored-or-derived-inside-the-components-above).

---

## 1. Sparkle — MIT

Used for in-app auto-update. Embedded at `Contents/Frameworks/Sparkle.framework`.
Homepage: <https://sparkle-project.org>. Version: 2.9.1.

Sparkle's licence file names its copyright holders and then sets out the separate
licences of five components vendored inside Sparkle (bsdiff, sais-lite, a portable
Ed25519 implementation, and `SUSignatureVerifier.m`). It is reproduced in full and
verbatim below, as the MIT licence requires.

```
Copyright (c) 2006-2013 Andy Matuschak.
Copyright (c) 2009-2013 Elgato Systems GmbH.
Copyright (c) 2011-2014 Kornel Lesiński.
Copyright (c) 2015-2017 Mayur Pawashe.
Copyright (c) 2014 C.W. Betts.
Copyright (c) 2014 Petroules Corporation.
Copyright (c) 2014 Big Nerd Ranch.
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

=================
EXTERNAL LICENSES
=================

bspatch.c and bsdiff.c, from bsdiff 4.3 <http://www.daemonology.net/bsdiff/>:

Copyright 2003-2005 Colin Percival
All rights reserved

Redistribution and use in source and binary forms, with or without
modification, are permitted providing that the following conditions 
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

--

sais.c and sais.h, from sais-lite (2010/08/07) <https://sites.google.com/site/yuta256/sais>:

The sais-lite copyright is as follows:

Copyright (c) 2008-2010 Yuta Mori All Rights Reserved.

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

--

Portable C implementation of Ed25519, from https://github.com/orlp/ed25519

Copyright (c) 2015 Orson Peters <orsonpeters@gmail.com>

This software is provided 'as-is', without any express or implied warranty. In no event will the
authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial
applications, and to alter it and redistribute it freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the
   original software. If you use this software in a product, an acknowledgment in the product
   documentation would be appreciated but is not required.

2. Altered source versions must be plainly marked as such, and must not be misrepresented as
   being the original software.

3. This notice may not be removed or altered from any source distribution.

--

SUSignatureVerifier.m:

Copyright (c) 2011 Mark Hamlin.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted providing that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

---

## 2. Apache-2.0 components

The following components are licensed under the Apache License, Version 2.0. Six of
them additionally grant the Swift.org Runtime Library Exception (§2.2).

- **Hummingbird** 2.22.0 — <https://github.com/hummingbird-project/hummingbird>
- **AsyncHTTPClient** 1.33.1 — <https://github.com/swift-server/async-http-client>
- **Swift Algorithms** 1.2.1 — <https://github.com/apple/swift-algorithms> — with Runtime Library Exception
- **SwiftASN1** 1.7.0 — <https://github.com/apple/swift-asn1>
- **Swift Async Algorithms** 1.1.3 — <https://github.com/apple/swift-async-algorithms> — with Runtime Library Exception
- **Swift Atomics** 1.3.0 — <https://github.com/apple/swift-atomics> — with Runtime Library Exception
- **SwiftCertificates** 1.19.1 — <https://github.com/apple/swift-certificates>
- **Swift Collections** 1.5.0 — <https://github.com/apple/swift-collections> — with Runtime Library Exception
- **SwiftConfiguration** 1.2.0 — <https://github.com/apple/swift-configuration>
- **SwiftCrypto** 4.5.0 — <https://github.com/apple/swift-crypto>
- **Swift Distributed Tracing** 1.4.1 — <https://github.com/apple/swift-distributed-tracing>
- **Swift HTTP Structured Headers** 1.7.0 — <https://github.com/apple/swift-http-structured-headers>
- **Swift HTTP Types** 1.5.1 — <https://github.com/apple/swift-http-types>
- **SwiftLog** 1.12.0 — <https://github.com/apple/swift-log>
- **SwiftMetrics** 2.10.1 — <https://github.com/apple/swift-metrics>
- **SwiftNIO** 2.99.0 — <https://github.com/apple/swift-nio>
- **SwiftNIO Extras** 1.34.0 — <https://github.com/apple/swift-nio-extras>
- **SwiftNIO HTTP/2** 1.43.0 — <https://github.com/apple/swift-nio-http2>
- **SwiftNIO SSL** 2.37.0 — <https://github.com/apple/swift-nio-ssl>
- **SwiftNIO Transport Services** 1.28.0 — <https://github.com/apple/swift-nio-transport-services>
- **Swift Numerics** 1.1.1 — <https://github.com/apple/swift-numerics> — with Runtime Library Exception
- **Swift Service Context** 1.3.0 — <https://github.com/apple/swift-service-context>
- **Swift Service Lifecycle** 2.11.0 — <https://github.com/swift-server/swift-service-lifecycle>
- **Swift System** 1.6.4 — <https://github.com/apple/swift-system> — with Runtime Library Exception

### 2.1 Apache License 2.0 — full text

Apache-2.0 §4(a) requires that recipients of the work be given a copy of the
licence. All 24 components in §2 were compared against the copy below: each carries
the same Apache-2.0 text, differing only in immaterial whitespace, and the six RLE
packages append §2.2 to it. It is reproduced once here, verbatim from
`macos/Pulsar/.build/checkouts/swift-nio/LICENSE.txt`, and applies to all of them.

```

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

### 2.2 Runtime Library Exception to the Apache 2.0 License

Appended to the Apache-2.0 grant of: Swift Algorithms, Swift Async Algorithms,
Swift Atomics, Swift Collections, Swift Numerics, and Swift System. Verbatim from
`macos/Pulsar/.build/checkouts/swift-system/LICENSE.txt`.

```
## Runtime Library Exception to the Apache 2.0 License: ##


    As an exception, if you use this Software to compile your source code and
    portions of this Software are embedded into the binary product as a result,
    you may redistribute such product without providing attribution as would
    otherwise be required by Sections 4(a), 4(b) and 4(d) of the License.```

### 2.3 Required NOTICE content

Apache-2.0 §4(d) requires that the attribution notices carried in a component's
NOTICE file be reproduced in the distributions of any derivative work. Each NOTICE
shipped by the components above is reproduced below, verbatim and unaltered.

Components in §2 that ship no NOTICE file, and so require no §4(d) content:
Swift Algorithms, Swift Async Algorithms, Swift Atomics, Swift Collections,
Swift Distributed Tracing, Swift HTTP Structured Headers, SwiftNIO Transport
Services, Swift Numerics, Swift System.

#### Hummingbird — `NOTICE.txt`

```
                            The Hummingbird Project
                            ====================

Please visit the Hummingbird web site for more information:

  * https://hummingbird.codes

Copyright 2024 The Hummingbird Project

The Hummingbird Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

-------------------------------------------------------------------------------

This product contains code from swift-foundation.

  * LICENSE (MIT):
    * https://github.com/swiftlang/swift-foundation/blob/main/LICENSE.md
  * HOMEPAGE:
    * https://github.com/swiftlang/swift-foundation/

```

#### AsyncHTTPClient — `NOTICE.txt`

```

                            The AsyncHTTPClient Project
                            ===========================

Please visit the AsyncHTTPClient web site for more information:

  * https://github.com/swift-server/async-http-client

Copyright 2017-2021 The AsyncHTTPClient Project

The AsyncHTTPClient Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

---

This product contains derivations of various scripts from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
    
---
    
This product contains a derivation of "XCTest+AsyncAwait.swift" from gRPC Swift.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/grpc/grpc-swift

---

This product contains a derivation of the Tony Stone's 'process_test_files.rb'.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/tonystone/build-tools/commit/6c417b7569df24597a48a9aa7b505b636e8f73a1
    * https://github.com/tonystone/build-tools/blob/cf3440f43bde2053430285b4ed0709c865892eb5/source/xctest_tool.rb

---

This product contains a derivation of Fabian Fett's 'Base64.swift'.

  * LICENSE (Apache License 2.0):
    * https://github.com/swift-extras/swift-extras-base64/blob/b8af49699d59ad065b801715a5009619100245ca/LICENSE
  * HOMEPAGE:
    * https://github.com/fabianfett/swift-base64-kit
```

#### SwiftASN1 — `NOTICE.txt`

```

                            The SwiftASN1 Project
                            =====================

Please visit the SwiftASN1 web site for more information:

  * https://github.com/apple/swift-asn1

Copyright 2022 The SwiftASN1 Project

The SwiftASN1 Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

---

This product contains derivations of various scripts from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
    
---

This product contains derivations of various scripts from Swift OpenAPI Generator.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-openapi-generator
```

#### SwiftCertificates — `NOTICE.txt`

```

                            The SwiftCertificates Project
                            =====================

Please visit the SwiftCertificates web site for more information:

  * https://github.com/apple/swift-certificates

Copyright 2022 The SwiftCertificates Project

The SwiftCertificates Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

---

This product contains derivations of various scripts from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
    
---

This product contains test data derived from Webpki.

  * LICENSE (ISC):
    * https://github.com/briansmith/webpki/blob/main/LICENSE
  * HOMEPAGE:
    * https://github.com/briansmith/webpki/
    
---

This product contains derivations of various ASN1 types from SwiftASN1.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-asn1

---

This product contains test vectors from pyca/cryptography.

  * LICENSE (Apache License 2.0):
    * https://github.com/pyca/cryptography/blob/main/LICENSE.APACHE
  * HOMEPAGE:
    * https://github.com/pyca/cryptography

---

This product contains code to calculate and decompose UNIX timestamps derived from musl libc.

  * LICENSE (MIT):
    * https://git.musl-libc.org/cgit/musl/tree/COPYRIGHT
  * HOMEPAGE:
    * https://musl.libc.org
    
---
    
This product contains derivations of various scripts from SwiftNIO SSH.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio-ssh
    
---

This product contains derivations of various scripts from Swift OpenAPI Generator.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-openapi-generator
```

#### SwiftConfiguration — `NOTICE.txt`

```

                       The SwiftConfiguration Project
                       =================================

Please visit the SwiftConfiguration web site for more information:

  * https://github.com/apple/swift-configuration

Copyright 2025 The SwiftConfiguration Project

The SwiftConfiguration Project licenses this file to you under the Apache
License, version 2.0 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This repository contains the gyb script from the swiftlang/swift repository.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/swiftlang/swift

---

This repository contains a modified copy of the test-examples.sh script the apple/swift-openapi-generator repository.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-openapi-generator

---
```

#### SwiftCrypto — `NOTICE.txt`

```
                            The SwiftCrypto Project
                            =======================

Please visit the SwiftCrypto web site for more information:

  * https://github.com/apple/swift-crypto

Copyright 2019 The SwiftCrypto Project

The SwiftCrypto Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product contains test vectors from Google's wycheproof project.

  * LICENSE (Apache License 2.0):
    * https://github.com/C2SP/wycheproof/blob/31387e2cd596587c859c611027b6a44d2e2b65ff/LICENSE
  * HOMEPAGE:
    * https://github.com/google/wycheproof

---

This product contains a derivation of various files from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
```

#### Swift HTTP Types — `NOTICE.txt`

```

                            The Swift HTTP Types Project
                            ====================================

Please visit the Swift HTTP Types web site for more information:

  * https://github.com/apple/swift-http-types

Copyright 2023 The Swift HTTP Types Project

The Swift HTTP Types Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product contains a derivation of various scripts from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
```

#### SwiftLog — `NOTICE.txt`

```

                            The SwiftLog Project
                            ========================

Please visit the SwiftLog web site for more information:

  * https://github.com/apple/swift-log

Copyright 2018, 2019 The SwiftLog Project

The SwiftLog Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product contains a derivation of the lock implementation and various
scripts from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
```

#### SwiftMetrics — `NOTICE.txt`

```

                            The SwiftMetrics Project
                            ========================

Please visit the SwiftMetrics web site for more information:

  * https://github.com/apple/swift-metrics

Copyright 2018, 2019 The SwiftMetrics Project

The SwiftMetrics Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product contains a derivation of the lock implementation and various scripts from SwiftNIO.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-nio
```

#### SwiftNIO — `NOTICE.txt`

```

                            The SwiftNIO Project
                            ====================

Please visit the SwiftNIO web site for more information:

  * https://github.com/apple/swift-nio

Copyright 2017, 2018 The SwiftNIO Project

The SwiftNIO Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product is heavily influenced by Netty.

  * LICENSE (Apache License 2.0):
    * https://github.com/netty/netty/blob/4.1/LICENSE.txt
  * HOMEPAGE:
    * https://netty.io

---

This product contains NodeJS's llhttp.

  * LICENSE (MIT):
    * https://github.com/nodejs/llhttp/blob/1e1c5b43326494e97cf8244ff57475eb72a1b62c/LICENSE-MIT
  * HOMEPAGE:
    * https://github.com/nodejs/llhttp

---

This product contains "cpp_magic.h" from Thomas Nixon & Jonathan Heathcote's uSHET

  * LICENSE (MIT):
    * https://github.com/18sg/uSHET/blob/c09e0acafd86720efe42dc15c63e0cc228244c32/lib/cpp_magic.h
  * HOMEPAGE:
    * https://github.com/18sg/uSHET

---

This product contains "sha1.c" and "sha1.h" from FreeBSD (Copyright (C) 1995, 1996, 1997, and 1998 WIDE Project)

  * LICENSE (BSD-3):
    * https://opensource.org/licenses/BSD-3-Clause
  * HOMEPAGE:
    * https://github.com/freebsd/freebsd-src

---

This product contains a derivation of Fabian Fett's 'Base64.swift'.

  * LICENSE (Apache License 2.0):
    * https://github.com/swift-extras/swift-extras-base64/blob/b8af49699d59ad065b801715a5009619100245ca/LICENSE
  * HOMEPAGE:
    * https://github.com/fabianfett/swift-base64-kit

---

This product contains a derivation of "XCTest+AsyncAwait.swift" & "StructuredConcurrencyHelpers" from AsyncHTTPClient.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/swift-server/async-http-client

---

This product contains a derivation of "_TinyArray.swift" from SwiftCertificates.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-certificates

---

This product contains a derivation of the mocking infrastructure from Swift System.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-system

---

This product contains a derivation of "TokenBucket.swift" from Swift Package Manager.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/swiftlang/swift-package-manager
```

#### SwiftNIO Extras — `NOTICE.txt`

```

                            The SwiftNIO Project
                            ====================

Please visit the SwiftNIO web site for more information:

  * https://github.com/apple/swift-nio

Copyright 2017, 2018 The SwiftNIO Project

The SwiftNIO Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product contains a derivation of the Tony Stone's 'process_test_files.rb'.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://codegists.com/snippet/ruby/generate_xctest_linux_runnerrb_tonystone_ruby

---

This product contains a derivation of "HTTP1ProxyConnectHandler.swift" and accompanying tests from AsyncHTTPClient.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/swift-server/async-http-client

---

This product contains a vendored copy of zlib with symbols prefixed as "cnioextras_z_".

  * LICENSE (zlib License):
    * https://www.zlib.net/zlib_license.html
  * HOMEPAGE:
    * https://www.zlib.net/

---
```

#### SwiftNIO HTTP/2 — `NOTICE.txt`

```

                            The SwiftNIO Project
                            ====================

Please visit the SwiftNIO web site for more information:

  * https://github.com/apple/swift-nio

Copyright 2017, 2018 The SwiftNIO Project

The SwiftNIO Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product is heavily influenced by Netty.

  * LICENSE (Apache License 2.0):
    * https://github.com/netty/netty/blob/4.1/LICENSE.txt
  * HOMEPAGE:
    * https://netty.io

---

This product contains a derivation of the Tony Stone's 'process_test_files.rb'.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://codegists.com/snippet/ruby/generate_xctest_linux_runnerrb_tonystone_ruby

---

The unit tests make use of 'hpack-test-case' by jxck, summerwind, kazu-yamamoto, and tatsuhiro-t.

  * LICENSE (MIT):
    * https://opensource.org/licenses/MIT
  * HOMEPAGE:
    * https://github.com/http2jp/hpack-test-case

---

This product contains a fuzz testing harness derived from Swift Protobuf.

  * LICENSE (Apache License 2.0):
    * https://github.com/apple/swift-protobuf/blob/main/LICENSE.txt
  * HOMEPAGE:
    * https://github.com/apple/swift-protobuf

---

This product contains a graceful shutdown connection manager derived from gRPC Swift NIO Transport.

  * LICENSE (Apache License 2.0):
    * https://github.com/grpc/grpc-swift-nio-transport/blob/main/LICENSE
  * HOMEPAGE:
    * https://github.com/gRPC/gRPC-swift-nio-transport
```

#### SwiftNIO SSL — `NOTICE.txt`

```

                            The SwiftNIO Project
                            ====================

Please visit the SwiftNIO web site for more information:

  * https://github.com/apple/swift-nio

Copyright 2017, 2018 The SwiftNIO Project

The SwiftNIO Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.<component>.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

-------------------------------------------------------------------------------

This product is heavily influenced by Netty.

  * LICENSE (Apache License 2.0):
    * https://github.com/netty/netty/blob/4.1/LICENSE.txt
  * HOMEPAGE:
    * https://netty.io

---

This product contains a derivation of the Tony Stone's 'process_test_files.rb'.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://codegists.com/snippet/ruby/generate_xctest_linux_runnerrb_tonystone_ruby

---

This product contains code derived from grpc-swift.

  * LICENSE (Apache License 2.0):
    * https://github.com/grpc/grpc-swift/blob/0.7.0/LICENSE
  * HOMEPAGE:
    * https://github.com/grpc/grpc-swift

---

This product contains code from boringssl.

  * LICENSE (Combination ISC and OpenSSL license)
    * https://boringssl.googlesource.com/boringssl/+/refs/heads/master/LICENSE
  * HOMEPAGE:
    * https://boringssl.googlesource.com/boringssl/

```

#### Swift Service Context — `NOTICE.txt`

```

                      The Swift Service Context Project
                            =====================

Please visit the Swift Service Context web site for more information:

  * https://github.com/apple/swift-asn1

Copyright 2024 The Swift Service Context Project

The Swift Service Context Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

---

This product contains derivations of benchmarking code from Swift Distributed Tracing.

  * LICENSE (Apache License 2.0):
    * https://www.apache.org/licenses/LICENSE-2.0
  * HOMEPAGE:
    * https://github.com/apple/swift-distributed-tracing    
```

#### Swift Service Lifecycle — `NOTICE.txt`

```

The ServiceLifecycle Project
===========================

Please visit the ServiceLifecycle web site for more information:

* https://github.com/swift-server/swift-service-lifecycle

Copyright 2019-2023 The ServiceLifecycle Project

The ServiceLifecycle Project licenses this file to you under the Apache License,
version 2.0 (the "License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at:

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.

Also, please refer to each LICENSE.txt file, which is located in
the 'license' directory of the distribution file, for the license terms of the
components that this product depends on.

---

This product contains derivations of the Lock and LockedValueBox implementations from SwiftNIO.

* LICENSE (Apache License 2.0):
* https://www.apache.org/licenses/LICENSE-2.0
* HOMEPAGE:
* https://github.com/apple/swift-nio

---

This product uses swift-async-algorithms.

* LICENSE (Apache License 2.0):
* https://www.apache.org/licenses/LICENSE-2.0
* HOMEPAGE:
* https://github.com/apple/swift-async-algorithms

---
```

---

## 3. Code vendored or derived inside the components above

The Apache-2.0 components above carry code from other projects, under other
licences. The attribution each of those requires travels in its parent's NOTICE
file, reproduced verbatim in §2.3; this section is the plain-language index of what
is in there, so nothing is buried.

| Code | Licence | Carried by | Upstream |
|---|---|---|---|
| BoringSSL (vendored C, symbol-prefixed) | Combination ISC and OpenSSL licence | SwiftNIO SSL (`CNIOBoringSSL`), SwiftCrypto (`CCryptoBoringSSL`) | upstream licence text vendored at [`third-party-licenses/BoringSSL-LICENSE.txt`](third-party-licenses/BoringSSL-LICENSE.txt) |
| llhttp (Node.js HTTP parser) | MIT | SwiftNIO (`CNIOLLHTTP`) | <https://github.com/nodejs/llhttp/blob/1e1c5b43326494e97cf8244ff57475eb72a1b62c/LICENSE-MIT> |
| zlib (vendored, symbols prefixed `cnioextras_z_`) | zlib licence | SwiftNIO Extras (`CNIOExtrasZlib`) | <https://www.zlib.net/zlib_license.html> |
| `sha1.c` / `sha1.h` — Copyright (C) 1995, 1996, 1997, 1998 WIDE Project | BSD-3-Clause | SwiftNIO (`CNIOSHA1`) | <https://github.com/freebsd/freebsd-src> |
| `cpp_magic.h` — Thomas Nixon & Jonathan Heathcote, uSHET | MIT | SwiftNIO | <https://github.com/18sg/uSHET/blob/c09e0acafd86720efe42dc15c63e0cc228244c32/lib/cpp_magic.h> |
| Fabian Fett's `Base64.swift` (swift-extras-base64) | Apache-2.0 | SwiftNIO (`_NIOBase64`), AsyncHTTPClient | <https://github.com/fabianfett/swift-base64-kit> |
| UNIX timestamp calculation derived from musl libc | MIT | SwiftCertificates | <https://git.musl-libc.org/cgit/musl/tree/COPYRIGHT> |
| Code from swift-foundation | MIT | Hummingbird | <https://github.com/swiftlang/swift-foundation/blob/main/LICENSE.md> |
| XKCP — eXtended Keccak Code Package (SHA-3 / Keccak permutations) | CC0 / public-domain waiver by the implementers | SwiftCrypto (`CXKCP`) | <https://keccak.team/> |
| Derivations from Netty, gRPC Swift, swift-protobuf, Swift Package Manager, Swift OpenAPI Generator, SwiftNIO SSH, swift-asn1 | Apache-2.0 | SwiftNIO, SwiftNIO HTTP/2, SwiftNIO SSL, SwiftCertificates, SwiftConfiguration, SwiftASN1, Swift Service Context | see the parent NOTICE in §2.3 |

### 3.1 BoringSSL — copyright holders in the vendored sources

BoringSSL is the largest body of third-party code Pulsar ships, vendored twice with
prefixed symbols: as `CNIOBoringSSL` inside SwiftNIO SSL and as `CCryptoBoringSSL`
inside SwiftCrypto. Neither vendoring carries a copy of BoringSSL's licence text in
its Swift package, so the canonical text is referenced rather than reproduced:
<https://boringssl.googlesource.com/boringssl/+/refs/heads/master/LICENSE> — a
combination of the ISC licence and the OpenSSL licence.

The copyright notices carried in the vendored source files name the following
holders. This list was read from the file headers in
`macos/Pulsar/.build/checkouts/{swift-nio-ssl,swift-crypto}`:

- The BoringSSL Authors (2014–2025)
- The OpenSSL Project Authors (1995–2021, across many files)
- Apple Inc. and the SwiftNIO project authors; Apple Inc. and the SwiftCrypto project authors
- Intel Corporation (2012, 2014, 2015)
- Arm Ltd. (2020)
- Oracle and/or its affiliates (2002)
- Nokia (2005)
- Network Resonance, Inc. (2006); RTFM, Inc. (2011)
- the HRSS authors (2017)
- Brian Smith (2016)
- Robert Nagy (2022)
- `third_party/fiat` — machine-generated field arithmetic from the fiat-crypto
  project. The vendored files carry a generator provenance comment and no
  copyright header of their own; upstream licence: <https://github.com/mit-plv/fiat-crypto>

Test-only material named in those NOTICE files — Google's wycheproof vectors, the
`hpack-test-case` fixtures, webpki test data, pyca/cryptography vectors, Tony
Stone's `process_test_files.rb` — is not compiled into the shipped binary. It is
left in the reproduced notices above because the licences do not permit trimming
them, and it is flagged here so the shipped-code picture stays honest.

---

## 4. Upstream project — speak

Pulsar began as a fork of [speak](https://github.com/tomc98/speak) by Thomas
Csere, MIT-licensed. That grant is intact and is the first copyright line of
[`LICENSE`](LICENSE) — Copyright (c) 2025 Thomas Csere — alongside the copyright in
the substantial work since. No separate reproduction is needed here: the root
`LICENSE` carries the full MIT text that covers it.

---

## 5. Apple system frameworks

Speech synthesis (`say` / AVFoundation), the menu-bar and window surfaces
(AppKit, SwiftUI), and the networking stack are macOS system frameworks. They are
linked against, not redistributed, and their use is governed by the macOS software
licence agreement rather than by any notice reproduced here.


---

## 6. MLX — MIT

Kokoro, Pulsar's opt-in on-device neural voice, runs on Apple's MLX. Two MLX
artefacts are distributed with the app:

- **MLX Swift 0.31.3** — statically linked into `Pulsar.app/Contents/MacOS/Pulsar`,
  reaching the build graph transitively through the vendored `kokoro-swift` package.
  It bundles MLX C++ 0.31.1 as a git submodule under the same MIT grant.
- **`mlx.metallib` (MLX 0.31.1)** — the precompiled Metal shader library, copied
  into `Pulsar.app/Contents/MacOS/mlx.metallib` by `scripts/build-pulsar-app.sh`.
  It is fetched from the `mlx-metal` distribution on PyPI, which repackages the
  shaders built from the same MIT-licensed MLX sources. This is a **redistributed
  binary**, which is why it is noticed here rather than treated as a build tool.

The version pin matters and is not cosmetic: the metallib must match the MLX C++
version that MLX Swift vendors, or kernels resolve at runtime and fail. Both are
0.31.1 today.

```
MIT License

Copyright (c) 2023 ml-explore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
