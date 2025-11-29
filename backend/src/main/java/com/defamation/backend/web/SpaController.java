// backend/src/main/java/.../web/SpaController.java
package com.defamation.backend.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class SpaController {

    // API, Swagger 같은 백엔드 경로는 제외하고,
    // 나머지 프론트 라우트(/cases, /history 등)는 전부 index.html로 포워딩
    @GetMapping(value = {
            "/cases",
    })
    public String forwardSpaRoutes() {
        return "forward:/index.html";
    }
}