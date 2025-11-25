package com.defamation.backend.service;

import com.defamation.backend.config.DefamationProperties;
import com.defamation.backend.domain.ClassificationRequest;
import com.defamation.backend.repository.ClassificationRequestRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class DefamationPredictService {

    private final DefamationProperties props;
    private final ClassificationRequestRepository clsRepo;

    private final ObjectMapper om = new ObjectMapper();
    private final RestTemplate rt = new RestTemplate();

    public String predictAndSave(Long modelId, String inputs) {
        String url = props.getModelEndpoints().get(modelId);

        // ✅ 지원 여부 체크
        if (url == null || url.isBlank()) {
            throw new UnsupportedModelException(modelId);
        }

        // FastAPI body는 inputs만
        Map<String, Object> body = Map.of("inputs", inputs);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        ResponseEntity<Map> resp = rt.postForEntity(url, entity, Map.class);

        if (!resp.getStatusCode().is2xxSuccessful() || resp.getBody() == null) {
            throw new RuntimeException("FastAPI 응답이 비정상입니다.");
        }

        String generatedText = String.valueOf(resp.getBody().get("generated_text")).trim();

        // ---------- 저장 ----------
        ClassificationRequest req = ClassificationRequest.builder()
                .problemSituation(inputs)
                .modelId(modelId)
                .build();

        try {
            JsonNode root = om.readTree(generatedText);

            req.setSentenceJudgment(text(root, "판단"));

            JsonNode s = root.path("형량");
            req.setSentenceType(text(s, "형종"));
            req.setSentenceValue(longOrNull(s, "벌금액"));
            req.setSentenceSuspension(intOrNull(s, "집행유예_기간_월"));
            req.setSentenceAdditionalOrder(text(s, "추가_조건"));
            req.setSentenceReason(text(root, "양형이유"));

            JsonNode crimes = root.get("죄명");
            if (crimes != null && crimes.isArray()) {
                req.setCaseNames(om.writeValueAsString(crimes));
            }
        } catch (Exception ignore) {
            // 파싱 실패해도 최소 입력/모델ID는 저장
        }

        clsRepo.save(req);
        return generatedText;
    }

    private static String text(JsonNode node, String key) {
        if (node == null) return null;
        JsonNode v = node.get(key);
        if (v == null || v.isNull()) return null;
        return v.asText();
    }

    private static Long longOrNull(JsonNode node, String key) {
        if (node == null) return null;
        JsonNode v = node.get(key);
        if (v == null || v.isNull()) return null;
        try { return v.asLong(); } catch (Exception e) { return null; }
    }

    private static Integer intOrNull(JsonNode node, String key) {
        if (node == null) return null;
        JsonNode v = node.get(key);
        if (v == null || v.isNull()) return null;
        try { return v.asInt(); } catch (Exception e) { return null; }
    }

    // ✅ 지원 안 하는 modelId면 튕기는 예외
    public static class UnsupportedModelException extends RuntimeException {
        public UnsupportedModelException(Long modelId) {
            super("지원하지 않는 model입니다: " + modelId);
        }
    }
}
