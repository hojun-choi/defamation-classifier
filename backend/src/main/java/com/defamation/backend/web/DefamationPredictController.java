package com.defamation.backend.web;

import com.defamation.backend.service.DefamationPredictService;
import com.defamation.backend.web.dto.PredictRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/defamation")
@RequiredArgsConstructor
public class DefamationPredictController {

    private final DefamationPredictService service;

    @PostMapping("/predict")
    public ResponseEntity<?> predict(@RequestBody PredictRequest req) {
        if (req.getInputs() == null || req.getInputs().isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("message", "inputs가 비어 있습니다."));
        }
        if (req.getModelId() == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "modelId가 필요합니다."));
        }

        try {
            String generated = service.predictAndSave(req.getModelId(), req.getInputs());
            return ResponseEntity.ok(Map.of("generated_text", generated));
        } catch (DefamationPredictService.UnsupportedModelException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(Map.of("message", e.getMessage()));
        }
    }
}
