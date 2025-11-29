package com.defamation.backend.web;

import com.defamation.backend.domain.Model;
import com.defamation.backend.service.DefamationModelService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/defamation")
@RequiredArgsConstructor
public class DefamationModelController {

    private final DefamationModelService defamationModelService;

    /**
     * GET /api/v1/defamation/models
     * enabled=1 인 모델 목록 반환
     */
    @GetMapping("/models")
    public List<Model> getModels() {
        return defamationModelService.getEnabledModels();
    }
}
